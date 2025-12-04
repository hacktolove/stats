# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_time, time_diff_in_seconds, time_diff, get_datetime, date_diff, flt, add_to_date, getdate, cint, get_link_to_form
from frappe.model.document import Document
from hrms.hr.doctype.shift_assignment.shift_assignment import get_employee_shift
from stats.hr_utils import is_from_time_in_shift_start_time_range, is_to_time_in_shift_end_time_range, create_employee_checkin, validate_deputy_employee_not_apply_for_same_dates


class EmployeeWorkOutofOfficeST(Document):
	def validate(self):
		self.validate_time_with_shift_time()
		self.calculate_total_hours()
		self.set_shift_start_end_time()
		self.validate_permission_hours_limit()
		self.validate_deputy_employee_if_applicable()

	# def on_submit(self):
	# 	self.create_employee_checkin_based_on_time()
	def validate_permission_hours_limit(self):
		permission_hours_limit = frappe.db.get_value("Stats Settings ST",None, "permission_hours_per_request")
		if permission_hours_limit and self.no_of_hour_per_day > 0:
			if self.no_of_hour_per_day > flt(permission_hours_limit):
				frappe.throw(_("You cannot request more than {0} hours per day").format(permission_hours_limit))
		else :
			frappe.throw(_("Please set Permission Hours Per Request in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))

	def validate_time_with_shift_time(self):
		if self.from_time and self.from_time:
			shift_type = frappe.db.get_value("Employee", self.employee_no, "default_shift")
			if shift_type:
				shift_time = frappe.db.get_value("Shift Type", shift_type, ["start_time", "end_time"], as_dict=True)
				if shift_time:
					consider_default_shift = True
					shift_details = get_employee_shift(self.employee_no, get_datetime(self.from_date), consider_default_shift, None)
					if shift_details:
						if self.from_time:
							if get_time(self.from_time) < get_time(shift_details.actual_start):
								frappe.throw(_(f"Permission time should be within the shift time: {get_time(shift_details.actual_start)} - {get_time(shift_details.actual_end)}"))
						if self.to_time:
							if get_time(self.to_time) > get_time(shift_details.actual_end):
								frappe.throw(_(f"Permission time should be within the shift time: {get_time(shift_details.actual_start)} - {get_time(shift_details.actual_end)}"))
			else:
				frappe.throw(_("Please set Default Shift for employee {0}".format(self.employee_no)))
	def validate_deputy_employee_if_applicable(self):
		apply_deputy_for_manager = frappe.db.get_single_value("Stats Settings ST", "apply_deputy_for_manager")
		apply_deputy_for_employee = frappe.db.get_single_value("Stats Settings ST", "apply_deputy_for_employee")
		is_applicable_for_deputy = self.is_manager
		no_of_days_required_for_deputy = frappe.db.get_single_value("Stats Settings ST", "deputy_required_for_no_of_days_of_work_out_office")
		if (is_applicable_for_deputy == 1 and is_applicable_for_deputy == apply_deputy_for_manager) or (is_applicable_for_deputy == 0 and is_applicable_for_deputy != apply_deputy_for_employee):
			if no_of_days_required_for_deputy:
				if cint(self.no_of_days) >= no_of_days_required_for_deputy:
					if self.deputy_employee == "" or self.deputy_employee == None:
						frappe.throw(_("Deputy Employee is mandatory when total no of days is greater than or equal to {0}".format(no_of_days_required_for_deputy)))
					else:
						deputy_employee_status = frappe.db.get_value("Employee", self.deputy_employee, "status")
						if deputy_employee_status != "Active":
							frappe.throw(_("Deputy Employee <b>{0}</b> is not active. Please select an active employee.".format(self.deputy_employee_name)))
						if self.deputy_employee == self.employee_no:
							frappe.throw(_("Deputy Employee and Employee can not be same. Please select different employee as Deputy Employee."))
						else :
							work_out_of_office_data = frappe.db.sql(
									"""
									select
										name, from_date, to_date, no_of_days
									from `tabEmployee Work Out of Office ST`
									where employee_no = %(employee)s and docstatus < 2
									and to_date >= %(from_date)s and from_date <= %(to_date)s
									""",
									{
										"employee": self.deputy_employee,
										"from_date": self.from_date,
										"to_date": self.to_date,
									},
									as_dict=1,
								)
							if len(work_out_of_office_data) > 0:
								for d in work_out_of_office_data:
									frappe.throw(_("Deputy Employee <b>{0}({1})</b> already has a work out of office request from {2} to {3} for {4} days.".format(
										self.deputy_employee,self.deputy_employee_name, d.from_date, d.to_date, d.no_of_days)))
									
							### check if deputy employee is not applying leave application for same dates
							validate_deputy_employee_not_apply_for_same_dates(self.from_date, self.to_date, self.deputy_employee)

						frappe.msgprint(_("Deputy Employee is not apply for work out of office for these dates"),indicator="green",alert=True)
			else:
				frappe.throw(_("Please set Deputy Required for No of Days of Leave in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
			
	def set_shift_start_end_time(self):
		if self.from_time:
			from_time_in_start_time_range, shift_start_time, shift_actual_start_time = is_from_time_in_shift_start_time_range(self.employee_no,self.from_date,self.from_time,validate=True)
			self.shift_start_time=shift_start_time
			self.shift_early_start_time=shift_actual_start_time
			if from_time_in_start_time_range==True:
				self.applicable_to_create_auto_employee_checkin="Yes"
			else:
				self.applicable_to_create_auto_employee_checkin="No"
		if self.to_time:
			to_time_in_end_time_range, shift_end_time, shift_early_end_time = is_to_time_in_shift_end_time_range(self.employee_no,self.from_date,self.to_time,self.shift_type,self.contract_type,validate=True)
			self.shift_end_time=shift_end_time
			self.shift_early_end_time=shift_early_end_time
			if to_time_in_end_time_range==True:
				self.applicable_to_create_auto_employee_checkin="Yes"
			else:
				self.applicable_to_create_auto_employee_checkin="No"

	def calculate_total_hours(self):
		if self.from_date and self.to_date:
			no_of_days = date_diff(self.to_date,self.from_date) + 1
			self.no_of_days = no_of_days
		if self.from_time and self.to_time:
			total_seconds = time_diff_in_seconds(self.to_time, self.from_time)
			self.no_of_hour_per_day = total_seconds/3600
		else:
			self.no_of_hour_per_day = 0
		print(self.no_of_hour_per_day,self.no_of_days,self.no_of_hour_per_day * self.no_of_days)
		self.total_minutes_per_day = flt(self.no_of_hour_per_day) * 60
		self.total_no_of_hour = self.no_of_hour_per_day * self.no_of_days

	def create_employee_checkin_based_on_time(self):
		for day in range(self.no_of_days):
			print(day,"--day")
			checkin_date = getdate(add_to_date(self.from_date,days=day))
			if self.from_time:
				from_time_in_start_time_range, permission_request_from_datetime = is_from_time_in_shift_start_time_range(self.employee_no,checkin_date,self.from_time,validate=False)
				if from_time_in_start_time_range == True :
					create_employee_checkin(self.employee_no, self.shift_type, "IN", permission_request_from_datetime, self.doctype, self.name)

			if self.to_time:
				to_time_in_end_time_range, permission_request_to_datetime = is_to_time_in_shift_end_time_range(self.employee_no,checkin_date,self.to_time,self.shift_type,self.contract_type,validate=False)
				if to_time_in_end_time_range == True:
					create_employee_checkin(self.employee_no, self.shift_type, "OUT", permission_request_to_datetime, self.doctype, self.name)