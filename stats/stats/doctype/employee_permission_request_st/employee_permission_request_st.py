# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_time, time_diff_in_seconds, time_diff, get_datetime, date_diff, cstr, get_link_to_form, flt, cint, get_last_day, getdate, today
from frappe.model.document import Document
from hrms.hr.doctype.shift_assignment.shift_assignment import get_employee_shift
from stats.hr_utils import is_from_time_in_shift_start_time_range, is_to_time_in_shift_end_time_range, create_employee_checkin


class EmployeePermissionRequestST(Document):
	def validate(self):
		self.validate_duplicate_entry()
		self.validate_date_with_type_of_request()
		self.validate_time_with_shift_time()
		self.calculate_total_hours()
		self.validate_working_hours_limit()
		self.validate_requested_minutes_with_balance()
		# self.set_shift_start_end_time()

	def on_submit(self):
		self.deduct_permission_balance_and_compensatory_balance_from_employee_if_applicable()

	def validate_time_with_shift_time(self):
		if self.from_time and self.to_time:
		# 	frappe.throw(_("You cannot put From time and To time both"))
		# elif self.from_time or self.to_time:
			if get_time(self.from_time) >= get_time(self.to_time):
				frappe.throw(_("From Time must be less than To Time"))
			shift_type = frappe.db.get_value("Employee", self.employee_no, "default_shift")
			if shift_type:
				shift_time = frappe.db.get_value("Shift Type", shift_type, ["start_time", "end_time"], as_dict=True)
				if shift_time:
					consider_default_shift = True
					shift_details = get_employee_shift(self.employee_no,get_datetime(self.request_date), consider_default_shift, None)
					if shift_details:
						if get_time(self.from_time) < get_time(shift_details.actual_start) or get_time(self.to_time) > get_time(shift_details.actual_end):
							frappe.throw(_(f"Permission time should be within the shift time: {get_time(shift_details.actual_start)} - {get_time(shift_details.actual_end)}"))
			else:
				frappe.throw(_("Please set Default Shift for employee {0}").format(self.employee_no))
	
	def validate_duplicate_entry(self):
		previous_record = frappe.db.exists("Employee Permission Request ST", {"employee_no":self.employee_no,"request_date":self.request_date,"type_of_request":self.type_of_request})
		if previous_record != None:
			if self.name != previous_record:
				frappe.throw(_("You have already created {0} on {1}").format(self.type_of_request,self.request_date))
	
	def validate_date_with_type_of_request(self):
		if self.type_of_request == _("Permission Request"):

			if getdate(self.request_date) < getdate(frappe.utils.today()):
				frappe.throw(_("Permission Request cannot be created for past date"))

			if self.consumption_type == _("Deduct From Permission Balance"):
				
				if self.contract == _("Civil"):
					current_month_end_date = get_last_day(self.creation_date)
					if getdate(self.request_date) > getdate(current_month_end_date):
						frappe.throw(_("You can apply for current month only"))
				
				if self.contract == _("Direct"):
					current_year = getdate(self.creation_date).year
					request_date_year = getdate(self.request_date).year
					if current_year != request_date_year:
						frappe.throw(_("You can apply for current year only"))

			elif self.consumption_type == _("Deduct From Compensatory Balance"):
				current_month_end_date = get_last_day(self.creation_date)
				if getdate(self.request_date) > getdate(current_month_end_date):
					frappe.throw(_("You can apply for current month only"))

		elif self.type_of_request == _("Reconciliation Request"):
			if getdate(self.request_date) >= getdate(frappe.utils.today()):
				frappe.throw(_("Reconciliation Request can only be created for past date"))
			
			if self.consumption_type == _("Deduct From Compensatory Balance"):
				current_month_end_date = get_last_day(self.creation_date)
				if getdate(self.request_date) > getdate(current_month_end_date):
					frappe.throw(_("You can apply for current month only"))
	
	def validate_working_hours_limit(self):
		permission_hours_limit = frappe.db.get_value("Stats Settings ST",None, "permission_hours_per_request")
		if permission_hours_limit and self.total_no_of_hour > 0:
			if self.total_no_of_hour > flt(permission_hours_limit):
				frappe.throw(_("You cannot request more than {0} hours in a single permission request").format(permission_hours_limit))
		else :
			frappe.throw(_("Please set Permission Hours Per Request in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
	
	def validate_requested_minutes_with_balance(self):
		if self.type_of_request == _("Permission Request"):
			if self.consumption_type == _("Deduct From Permission Balance"):
				if self.contract == _("Direct"):
					permission_balance_from_employee_profile =  frappe.db.get_value("Employee",self.employee_no,"custom_permission_balance_per_year")
					if self.total_minutes and cint(self.total_minutes) > cint(permission_balance_from_employee_profile):
						frappe.throw(_("You can not apply for {0} minutes.<br>Your remaining balance is {1} minutes".format(self.total_minutes,permission_balance_from_employee_profile)))
				elif self.contract == _("Civil"):
					permission_balance_from_employee_profile =  frappe.db.get_value("Employee",self.employee_no,"custom_permission_balance_per_monthcurrent")
					if self.total_minutes and cint(self.total_minutes) > cint(permission_balance_from_employee_profile):
						frappe.throw(_("You can not apply for {0} minutes.<br>Your remaining balance is {1} minutes".format(self.total_minutes,permission_balance_from_employee_profile)))

			elif self.consumption_type == _("Deduct From Compensatory Balance"):
				print("In Compensatory Balance")

				if getdate(self.request_date).month < getdate(today()).month:
					compensatory_balance_from_employee_profile =  frappe.db.get_value("Employee",self.employee_no,"custom_compensatory_balance__previous_month_")
					print(compensatory_balance_from_employee_profile,"<><><> previous")
				else:
					compensatory_balance_from_employee_profile =  frappe.db.get_value("Employee",self.employee_no,"custom_compensatory_balance__current_month__")
					print(compensatory_balance_from_employee_profile,"<><><> current")

				if self.total_minutes and cint(self.total_minutes) > cint(compensatory_balance_from_employee_profile):
					frappe.throw(_("You can not apply for {0} minutes.<br>Your remaining balance is {1} minutes".format(self.total_minutes,compensatory_balance_from_employee_profile)))
			
		elif self.type_of_request == _("Reconciliation Request"):
			if self.shortage_in_working_minutes > 0:
				if self.consumption_type == _("Deduct From Permission Balance"):
					if self.contract == _("Direct"):
						permission_balance_from_employee_profile =  frappe.db.get_value("Employee",self.employee_no,"custom_permission_balance_per_year")
						if self.shortage_in_working_minutes and cint(self.shortage_in_working_minutes) > cint(permission_balance_from_employee_profile):
							frappe.throw(_("You can not apply for {0} minutes.<br>Your remaining balance is {1} minutes".format(self.shortage_in_working_minutes,permission_balance_from_employee_profile)))
					elif self.contract == _("Civil"):
						permission_balance_from_employee_profile =  frappe.db.get_value("Employee",self.employee_no,"custom_permission_balance_per_monthprevious")
						if self.shortage_in_working_minutes and cint(self.shortage_in_working_minutes) > cint(permission_balance_from_employee_profile):
							frappe.throw(_("You can not apply for {0} minutes.<br>Your remaining balance is {1} minutes".format(self.shortage_in_working_minutes,permission_balance_from_employee_profile)))

				elif self.consumption_type == _("Deduct From Compensatory Balance"):
					print("In Compensatory Balance")
					if getdate(self.request_date).month < getdate(today()).month:
						compensatory_balance_from_employee_profile =  frappe.db.get_value("Employee",self.employee_no,"custom_compensatory_balance__previous_month_")
						print(compensatory_balance_from_employee_profile,"<><><> previous")
					else:
						compensatory_balance_from_employee_profile =  frappe.db.get_value("Employee",self.employee_no,"custom_compensatory_balance__current_month__")
						print(compensatory_balance_from_employee_profile,"<><><> current")

					if self.shortage_in_working_minutes and cint(self.shortage_in_working_minutes) > cint(compensatory_balance_from_employee_profile):
						frappe.throw(_("You can not apply for {0} minutes.<br>Your remaining balance is {1} minutes".format(self.shortage_in_working_minutes,compensatory_balance_from_employee_profile)))
			else :
				frappe.throw(_("No shortage found for the requested date. Hence you cannot appyly for Reconciliation Request"))
	
	def calculate_total_hours(self):
		if self.from_time and self.to_time:
			self.total_no_of_hour = time_diff_in_seconds(self.to_time, self.from_time)/3600
			self.total_minutes = time_diff_in_seconds(self.to_time, self.from_time) / 60
		else:
			self.total_no_of_hour = 0
			self.total_minutes = 0
		
	def set_shift_start_end_time(self):
		if self.from_time:
			from_time_in_start_time_range, shift_start_time, shift_actual_start_time = is_from_time_in_shift_start_time_range(self.employee_no,self.request_date,self.from_time,validate=True)
			self.shift_start_time=shift_start_time
			self.shift_early_start_time=shift_actual_start_time
			if from_time_in_start_time_range==True:
				self.applicable_to_create_auto_employee_checkin="Yes"
			else:
				self.applicable_to_create_auto_employee_checkin="No"
		if self.to_time:
			to_time_in_end_time_range, shift_end_time, shift_early_end_time = is_to_time_in_shift_end_time_range(self.employee_no,self.request_date,self.to_time,self.shift_type,self.contract_type,validate=True)
			self.shift_end_time=shift_end_time
			self.shift_early_end_time=shift_early_end_time
			if to_time_in_end_time_range==True:
				self.applicable_to_create_auto_employee_checkin="Yes"
			else:
				self.applicable_to_create_auto_employee_checkin="No"

	def create_employee_checkin_based_on_time(self):
		if self.from_time:
			from_time_in_start_time_range, permission_request_from_datetime = is_from_time_in_shift_start_time_range(self.employee_no,self.request_date,self.from_time,validate=False)
			if from_time_in_start_time_range == True :
				create_employee_checkin(self.employee_no, self.shift_type, "IN", permission_request_from_datetime, self.doctype, self.name)

		if self.to_time:
			to_time_in_end_time_range, permission_request_to_datetime = is_to_time_in_shift_end_time_range(self.employee_no,self.request_date,self.to_time,self.shift_type,self.contract_type,validate=False)
			if to_time_in_end_time_range == True:
				create_employee_checkin(self.employee_no, self.shift_type, "OUT", permission_request_to_datetime, self.doctype, self.name)

	@frappe.whitelist()
	def get_shortage_for_requested_date(self):
		attendance_details = frappe.db.get_all("Attendance",
										 filters={"employee":self.employee_no,"attendance_date":self.request_date},
										 fields=["custom_shortage_to_complete_working_hours","name"],limit=1)
		shortage_in_working_minutes = attendance_details[0].custom_shortage_to_complete_working_hours if len(attendance_details) > 0 else 0
		attendance_reference = attendance_details[0].name if len(attendance_details) > 0 else ""
	
		if shortage_in_working_minutes > 0:
			attendance_status = frappe.db.get_value("Attendance",attendance_reference,"status")
			if attendance_status == "Absent":
				print(attendance_status,"<<<<<>>>")
				frappe.throw(_("The attendance for the requested date is marked as Absent. Hence you cannot apply for Reconciliation Request"))

		return {"shortage_in_working_minutes":shortage_in_working_minutes,
		  "attendance_reference":attendance_reference}

	def deduct_permission_balance_and_compensatory_balance_from_employee_if_applicable(self):
		if self.type_of_request == "Reconciliation Request":

			### Update Attendance working minutes
			if self.attendance_reference :
				current_working_minutes = frappe.db.get_value("Attendance",self.attendance_reference,"custom_working_minutes_with_grace")
				working_minutes_after_update = current_working_minutes + self.shortage_in_working_minutes
				final_working_hours = working_minutes_after_update / 60

				frappe.db.set_value("Attendance", self.attendance_reference, "custom_working_minutes_with_grace", working_minutes_after_update)
				frappe.db.set_value("Attendance", self.attendance_reference, "working_hours", final_working_hours)
				frappe.db.set_value("Attendance", self.attendance_reference, "custom_shortage_to_complete_working_hours", 0)
				frappe.db.set_value("Attendance", self.attendance_reference, "custom_reconciliation_method", self.consumption_type)
				
				### Add Comment in Attendance
				attendance_doc = frappe.get_doc("Attendance",self.attendance_reference)
				attendance_doc.custom_balance_used_mins = self.shortage_in_working_minutes
				attendance_doc.custom_employee_permission_doctype = self.doctype
				attendance_doc.custom_employee_permission_reference = self.name
				attendance_doc.add_comment("Comment",text=_("Working Minutes ( With Grace ) are updated due to Employee Permission Request {0}".format(get_link_to_form("Employee Permission Request ST",self.name))))
				attendance_doc.save(ignore_permissions=True)

			### Deduct Balance from Employee Profile
			if self.consumption_type == "Deduct From Permission Balance":
				contract = frappe.db.get_value("Contract Type ST",self.contract_type,"contract")
				if contract == "Civil":
					if getdate(self.request_date).month == getdate(today()).month:
						employee_doc = frappe.get_doc("Employee",self.employee_no)
						remaining_balance = employee_doc.custom_permission_balance_per_monthcurrent - self.shortage_in_working_minutes
						employee_doc.add_comment("Comment",text=_("Permission Balance Per Month(Current) is deducted by {0} minutes due to Employee Permission Request {1}".format(self.shortage_in_working_minutes,get_link_to_form("Employee Permission Request ST",self.name))))
						employee_doc.flags.ignore_mandatory = True
						employee_doc.save(ignore_permissions=True)
						frappe.db.set_value("Employee", self.employee_no, "custom_permission_balance_per_monthcurrent", remaining_balance)
						frappe.msgprint(_("Shortage minutes are deducted from Employee Profile"),alert=True)
					
					elif getdate(self.request_date).month < getdate(today()).month:
						employee_doc = frappe.get_doc("Employee",self.employee_no)
						remaining_balance = employee_doc.custom_permission_balance_per_monthprevious - self.shortage_in_working_minutes
						employee_doc.add_comment("Comment",text=_("Permission Balance Per Month(Previous) is deducted by {0} minutes due to Employee Permission Request {1}".format(self.shortage_in_working_minutes,get_link_to_form("Employee Permission Request ST",self.name))))
						employee_doc.flags.ignore_mandatory = True
						employee_doc.save(ignore_permissions=True)
						frappe.db.set_value("Employee", self.employee_no, "custom_permission_balance_per_monthprevious", remaining_balance)
						frappe.msgprint(_("Shortage minutes are deducted from Employee Profile"),alert=True)

				elif contract == "Direct":
					employee_doc = frappe.get_doc("Employee",self.employee_no)
					remaining_balance = employee_doc.custom_permission_balance_per_year - self.shortage_in_working_minutes
					employee_doc.add_comment("Comment",text=_("Permission Balance Per Year is deducted by {0} minutes due to Employee Permission Request {1}".format(self.shortage_in_working_minutes,get_link_to_form("Employee Permission Request ST",self.name))))
					employee_doc.flags.ignore_mandatory = True
					employee_doc.save(ignore_permissions=True)
					frappe.db.set_value("Employee", self.employee_no, "custom_permission_balance_per_year", remaining_balance)
					frappe.msgprint(_("Shortage minutes are deducted from Employee Profile"),alert=True)
		
			if self.consumption_type == "Deduct From Compensatory Balance":
				if getdate(self.request_date).month == getdate(today()).month:
						employee_doc = frappe.get_doc("Employee",self.employee_no)
						remaining_balance = employee_doc.custom_compensatory_balance__current_month__ - self.shortage_in_working_minutes
						employee_doc.add_comment("Comment",text=_("Compensatory Balance ( Current Month ) is deducted by {0} minutes due to Employee Permission Request {1}".format(self.shortage_in_working_minutes,get_link_to_form("Employee Permission Request ST",self.name))))
						employee_doc.flags.ignore_mandatory = True
						employee_doc.save(ignore_permissions=True)
						frappe.db.set_value("Employee", self.employee_no, "custom_compensatory_balance__current_month__", remaining_balance)
						frappe.msgprint(_("Shortage minutes are deducted from Employee Profile"),alert=True)
					
				elif getdate(self.request_date).month < getdate(today()).month:
					employee_doc = frappe.get_doc("Employee",self.employee_no)
					remaining_balance = employee_doc.custom_compensatory_balance__previous_month_ - self.shortage_in_working_minutes
					employee_doc.add_comment("Comment",text=_("Compensatory Balance ( Previous Month ) is deducted by {0} minutes due to Employee Permission Request {1}".format(self.shortage_in_working_minutes,get_link_to_form("Employee Permission Request ST",self.name))))
					employee_doc.flags.ignore_mandatory = True
					employee_doc.save(ignore_permissions=True)
					frappe.db.set_value("Employee", self.employee_no, "custom_compensatory_balance__previous_month_", remaining_balance)
					frappe.msgprint(_("Shortage minutes are deducted from Employee Profile"),alert=True)