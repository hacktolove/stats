# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form, date_diff, add_to_date, get_datetime, get_date_str, cstr, time_diff_in_hours, getdate
from stats.hr_utils import check_if_holiday_between_applied_dates
from frappe.model.document import Document


class ScholarshipExtendST(Document):

	def validate(self):
		self.validate_return_date()

	def on_submit(self):
		self.create_future_attendance_for_scholarship_extended_date()
		self.delete_future_attendance_for_scholarship_extended_date()
		self.update_scholarship_end_date_in_request()

	def validate_return_date(self):
		if self.scholarship_end_date and self.extend_till_date:
			if self.extend_till_date <= self.scholarship_end_date:
				frappe.throw(_("Extend Till Date cannot be less than or equal to Scholarship End Date"))

	def update_scholarship_end_date_in_request(self):
		if self.scholarship_request_reference:
			scholarship_request_doc = frappe.get_doc("Scholarship Request ST",self.scholarship_request_reference)
			scholarship_request_doc.scholarship_end_date = self.extend_till_date
			scholarship_request_doc.add_comment("Comment",text=_("Scholarship End Date is extended due to Scholarship Extend request {0}".format(get_link_to_form("Scholarship Extend ST",self.name))))
			scholarship_request_doc.save(ignore_permissions=True)
			frappe.msgprint(_("Scholarship End Date is updated in Scholarship Request {0}".format(get_link_to_form("Scholarship Request ST",self.scholarship_request_reference))),alert=True)
	
	def create_future_attendance_for_scholarship_extended_date(self):
		if self.extend_till_date > self.plan_return_date:
			days = date_diff(self.extend_till_date,self.plan_return_date)
			permission_days = frappe.db.get_value("Scholarship ST",{"scholarship_no":self.scholarship_no},"permission_days")
			if permission_days and permission_days > 0:
				days = days + permission_days
		
			different_years_list = []
			for fiscal_year in range (getdate(self.plan_return_date).year, getdate(self.extend_till_date).year+1):
				if fiscal_year not in different_years_list:
					different_years_list.append(fiscal_year)

			yearly_holiday_list = []

			for year in different_years_list:
				holiday = {}
				fiscal_year_doc = frappe.get_doc("Fiscal Year",year)
				exist_holiday_list = frappe.db.get_all("Holiday List",
											filters={"to_date":fiscal_year_doc.year_end_date,"from_date":fiscal_year_doc.year_start_date},
											fields=["name"])
				if len(exist_holiday_list)<1:
					frappe.throw(_("Holiday list for year <b>{0}</b> does not exists. Hence we cannot create future attendance.").format(year))
				else :
					holiday["year"]=year
					holiday["holiday_list"]=exist_holiday_list[0].name
					yearly_holiday_list.append(holiday)
				
			for day in range (days):
				attendance_date = add_to_date(getdate(self.plan_return_date),days=day+1)
				check_holiday = None
				for ele in yearly_holiday_list:
					if attendance_date.year == ele.get("year"):
						check_holiday = check_if_holiday_between_applied_dates(self.employee_no,attendance_date,attendance_date,holiday_list=ele.get("holiday_list"))
				last_attendance_date = None
				if check_holiday == False:
					attendance_doc = frappe.new_doc("Attendance")
					attendance_doc.employee = self.employee_no
					attendance_doc.attendance_date = attendance_date
					attendance_doc.custom_attendance_type = "Scholarship"

					employee_shift = frappe.db.get_value("Employee",self.employee_no,"default_shift")
					shift_start_time = frappe.db.get_value("Shift Type",employee_shift,"start_time")
					shift_end_time = frappe.db.get_value("Shift Type",employee_shift,"end_time")

					in_time = get_datetime(get_date_str(attendance_date) + " " + cstr(shift_start_time))
					out_time = get_datetime(get_date_str(attendance_date) + " " + cstr(shift_end_time))
					total_working_hours = time_diff_in_hours(in_time, out_time)

					attendance_doc.shift = employee_shift
					attendance_doc.in_time = in_time
					attendance_doc.out_time = out_time
					attendance_doc.working_hours = total_working_hours
					attendance_doc.status = "Present"
					attendance_doc.save(ignore_permissions=True)
					attendance_doc.submit()
					last_attendance_date = attendance_date

			frappe.msgprint(_("Attendance from {0} to {1} is created.").format(self.plan_return_date,last_attendance_date),alert=True)
		
	def delete_future_attendance_for_scholarship_extended_date(self):
		if self.extend_till_date < self.plan_return_date:
			days = date_diff(self.plan_return_date,self.extend_till_date)
			for day in range (days+1):
				attendance_date = add_to_date(getdate(self.extend_till_date),days=day+1)
				attendance_name = frappe.db.get_value("Attendance",{"employee":self.employee_no,"attendance_date":attendance_date,"custom_attendance_type":"Scholarship"},"name")
				if attendance_name:
					attendance_doc = frappe.get_doc("Attendance",attendance_name)
					if attendance_doc.docstatus == 1:
						attendance_doc.cancel()
					attendance_doc.delete()
			frappe.msgprint(_("Attendance from {0} to {1} is deleted.").format(add_to_date(self.extend_till_date,days=1),self.plan_return_date),alert=True)