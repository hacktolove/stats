# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, cint, get_link_to_form, today, add_to_date, nowdate,flt, add_months
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday as holiday_between_applied_dates
from frappe.model.mapper import get_mapped_doc
from erpnext.accounts.utils import get_fiscal_year
from hrms.hr.doctype.leave_application.leave_application import get_holidays, get_leave_allocation_records, get_leave_balance_on, get_leaves_for_period, get_leaves_pending_approval_for_period, get_leave_approver
from stats.hr_utils import is_leave_year_valid, is_leave_applied_dates_within_leave_cycle_year, leave_allocation_exists_for_leave_cycle_year, validate_deputy_employee_not_apply_for_same_dates, is_fatal_leave_cycle_year_valid
from stats.api import get_doctype_workflow_state_list_for_progress_bar
class LeaveRequestST(Document):
	# def onload(self):
	# 	template_path = "templates/workflow_progressbar.html"
	# 	workflow_states =get_doctype_workflow_state_list_for_progress_bar(self.doctype)
	# 	html = frappe.render_template(template_path,  dict(workflow_states=workflow_states, doc=self.as_dict()))
	# 	self.set_onload("workflow_progressbar_html", html)
	# 	print("=====Helllo======="*10)

	def validate(self):
		self.validate_once_per_life_time_requests()     
		self.validate_relative()
		self.validate_attachments()
		self.calculate_to_date_based_on_no_of_days()
		self.validate_other_leave_consumed_days()
		self.validate_from_to_dates()
		self.validate_deputy_employee_if_applicable()
		self.validate_future_dates()
		self.validate_past_dates()
		self.calculate_total_days_and_yearly_days()
		self.validate_leave_type_with_no_of_days()
		self.validate_sick_leave_type()
	
	def validate_relative(self):
		value = frappe.db.get_value("Leave Type" , self.leave_type , "custom_require_relative")
		if(value == 1):
			if(self.custom_relative not in ["Father" , "Mother" , "Sister" , "Brother" , "Son" , "Daughter"]):
				frappe.throw("Please Add Relative")
		else:
			frappe.throw("me")




	
	def validate_sick_leave_type(self):
		if _(self.contract_type) == _("Direct"):
			first_sick_leave, second_sick_leave, third_sick_leave = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_direct","sick_leave_type_2_direct","sick_leave_type_3_direct"])
			if first_sick_leave and second_sick_leave and third_sick_leave:
				if self.leave_type in [first_sick_leave, second_sick_leave, third_sick_leave]:
				# if self.leave_type == first_sick_leave_type:
					leave_year, leave_cycle_start_date, leave_cycle_end_date = is_leave_year_valid(self.from_date,self.to_date,self.employee_no)
					if leave_year=="Exists":
						print("+"*10)
						leave_dates_between_leave_cycle_year = is_leave_applied_dates_within_leave_cycle_year(self.from_date,self.to_date,self.employee_no,leave_type="Sick Leave")
						print("===========validate", leave_dates_between_leave_cycle_year)
						if leave_dates_between_leave_cycle_year==True:
							leave_allocation_exists, leave_allocation_reference = leave_allocation_exists_for_leave_cycle_year(self.from_date, self.to_date, self.employee_no, self.leave_type)
							if leave_allocation_exists == True:
								used_leaves_in_leave_cycle_year = frappe.db.get_all("Leave Application",
																filters={"from_date":[">=",leave_cycle_start_date], "to_date":["<=",leave_cycle_end_date],"employee":self.employee_no,"leave_type":self.leave_type,"status":"Approved","docstatus":1},
																fields=["sum(total_leave_days) as total_leave_days"],group_by="employee")
								print(used_leaves_in_leave_cycle_year,"used_leaves_in_leave_cycle_year=========================")
								max_allowed_leaves = frappe.db.get_value("Leave Allocation", leave_allocation_reference, "total_leaves_allocated")
								if len(used_leaves_in_leave_cycle_year)>0:
									remaining_leaves = flt(max_allowed_leaves) - flt(used_leaves_in_leave_cycle_year[0].total_leave_days)
									if self.total_no_of_days > remaining_leaves:
										frappe.throw(_("You cannot applied for {0} days. You have {1} days are remaining of leave type {2}".format(self.total_no_of_days,remaining_leaves,self.leave_type)))
					if leave_year=="Future Dates":
						# No action required for future dates as per current business logic.
						pass
					if leave_year=="Accross The Year":
						frappe.throw(_("You cannot apply leave accross leave cycle year.<br><b>Details:</b><br>Leave Cycle Start Date : {0}<br>Leave Cycle End Date : {1}".format(leave_cycle_start_date, leave_cycle_end_date)))

			else: 
				frappe.throw(_("Please set Sick Types in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
		
		elif _(self.contract_type) == _("Civil"):
			first_sick_leave, second_sick_leave, third_sick_leave, fourth_sick_leave = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_civil","sick_leave_type_2_civil","sick_leave_type_3_civil","sick_leave_type_4_civil"])
			if first_sick_leave and second_sick_leave and third_sick_leave and fourth_sick_leave:
				if self.leave_type in [first_sick_leave, second_sick_leave, third_sick_leave, fourth_sick_leave]:
				# if self.leave_type == first_sick_leave_type:
					leave_year, leave_cycle_start_date, leave_cycle_end_date = is_leave_year_valid(self.from_date,self.to_date,self.employee_no)
					if leave_year=="Exists":
						print("+"*10)
						leave_dates_between_leave_cycle_year = is_leave_applied_dates_within_leave_cycle_year(self.from_date,self.to_date,self.employee_no,leave_type="Sick Leave")
						print("===========validate", leave_dates_between_leave_cycle_year)
						if leave_dates_between_leave_cycle_year==True:
							leave_allocation_exists, leave_allocation_reference = leave_allocation_exists_for_leave_cycle_year(self.from_date, self.to_date, self.employee_no, self.leave_type)
							if leave_allocation_exists == True:
								used_leaves_in_leave_cycle_year = frappe.db.get_all("Leave Application",
																filters={"from_date":[">=",leave_cycle_start_date], "to_date":["<=",leave_cycle_end_date],"employee":self.employee_no,"leave_type":self.leave_type,"status":"Approved","docstatus":1},
																fields=["sum(total_leave_days) as total_leave_days"],group_by="employee")
								print(used_leaves_in_leave_cycle_year,"used_leaves_in_leave_cycle_year=========================")
								max_allowed_leaves = frappe.db.get_value("Leave Allocation", leave_allocation_reference, "total_leaves_allocated")
								if len(used_leaves_in_leave_cycle_year)>0:
									remaining_leaves = flt(max_allowed_leaves) - flt(used_leaves_in_leave_cycle_year[0].total_leave_days)
									if self.total_no_of_days > remaining_leaves:
										frappe.throw(_("You cannot applied for {0} days. You have {1} days are remaining of leave type {2}".format(self.total_no_of_days,remaining_leaves,self.leave_type)))
					if leave_year=="Future Dates":
						# No action required for future dates as per current business logic.
						pass
					if leave_year=="Accross The Year":
						frappe.throw(_("You cannot apply leave accross leave cycle year.<br><b>Details:</b><br>Leave Cycle Start Date : {0}<br>Leave Cycle End Date : {1}".format(leave_cycle_start_date, leave_cycle_end_date)))
			else: 
				frappe.throw(_("Please set Sick Types in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
		
		### Fatal Sick Leave Type Validation
		
		first_fatal_sick_leave, second_fatal_sick_leave, third_fatal_sick_leave, fourth_fatal_sick_leave = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["fatal_sick_leave_type_1","fatal_sick_leave_type_2","fatal_sick_leave_type_3","fatal_sick_leave_type_4"])
		if first_fatal_sick_leave and second_fatal_sick_leave and third_fatal_sick_leave and fourth_fatal_sick_leave:
			if self.leave_type in [first_fatal_sick_leave, second_fatal_sick_leave, third_fatal_sick_leave, fourth_fatal_sick_leave]:
			# if self.leave_type == first_sick_leave_type:
				leave_year, leave_cycle_start_date, leave_cycle_end_date = is_fatal_leave_cycle_year_valid(self.from_date,self.to_date,self.employee_no)
				if leave_year=="Exists":
					print("+"*10)
					leave_dates_between_leave_cycle_year = is_leave_applied_dates_within_leave_cycle_year(self.from_date,self.to_date,self.employee_no,leave_type="Fatal Sick Leave")
					print("===========validate", leave_dates_between_leave_cycle_year)
					if leave_dates_between_leave_cycle_year==True:
						leave_allocation_exists, leave_allocation_reference = leave_allocation_exists_for_leave_cycle_year(self.from_date, self.to_date, self.employee_no, self.leave_type)
						if leave_allocation_exists == True:
							used_leaves_in_leave_cycle_year = frappe.db.get_all("Leave Application",
															filters={"from_date":[">=",leave_cycle_start_date], "to_date":["<=",leave_cycle_end_date],"employee":self.employee_no,"leave_type":self.leave_type,"status":"Approved","docstatus":1},
															fields=["sum(total_leave_days) as total_leave_days"],group_by="employee")
							print(used_leaves_in_leave_cycle_year,"used_leaves_in_leave_cycle_year=========================")
							max_allowed_leaves = frappe.db.get_value("Leave Allocation", leave_allocation_reference, "total_leaves_allocated")
							if len(used_leaves_in_leave_cycle_year)>0:
								remaining_leaves = flt(max_allowed_leaves) - flt(used_leaves_in_leave_cycle_year[0].total_leave_days)
								if self.total_no_of_days > remaining_leaves:
									frappe.throw(_("You cannot applied for {0} days. You have {1} days are remaining of leave type {2}".format(self.total_no_of_days,remaining_leaves,self.leave_type)))
				if leave_year=="Future Dates":
					# No action required for future dates as per current business logic.
					pass
				if leave_year=="Accross The Year":
					frappe.throw(_("You cannot apply leave accross leave cycle year.<br><b>Details:</b><br>Leave Cycle Start Date : {0}<br>Leave Cycle End Date : {1}".format(leave_cycle_start_date, leave_cycle_end_date)))
		else: 
			frappe.throw(_("Please set Fatal Sick Types in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))


	def on_submit(self):
		if not self.to_date:
			frappe.throw(_("To Date is mandatory"))
		if not self.leave_type:
			frappe.throw(_("Please Select Leave Type."))
		if self.status == "Pending":
			frappe.throw(_("Please Approve or Reject the request before submit"))
		if self.status == "Approved":
			sick_leave_list = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_direct","sick_leave_type_2_direct","sick_leave_type_3_direct",
																				 "sick_leave_type_1_civil","sick_leave_type_2_civil","sick_leave_type_3_civil","sick_leave_type_4_civil",
																				 "fatal_sick_leave_type_1","fatal_sick_leave_type_2","fatal_sick_leave_type_3","fatal_sick_leave_type_4"])
			print(sick_leave_list,"================first_sick_leave",type(sick_leave_list))
			if self.leave_type not in sick_leave_list:
				print("-----------------------")
				self.create_leave_allocation_and_application_based_on_days_per_year()
			else :
				self.create_leave_allocation_and_application_for_sick_leave_type()
	
	def on_cancel(self):
		all_normal_sick_leave_list = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_direct","sick_leave_type_2_direct","sick_leave_type_3_direct",
																				"sick_leave_type_1_civil","sick_leave_type_2_civil","sick_leave_type_3_civil","sick_leave_type_4_civil"])
		all_fatal_sick_leave_list = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["fatal_sick_leave_type_1","fatal_sick_leave_type_2","fatal_sick_leave_type_3","fatal_sick_leave_type_4"])
		first_sick_leave_list = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_direct","sick_leave_type_1_civil"])
		
		first_fatal_sick_leave = frappe.db.get_value("Stats Settings ST","Stats Settings ST","fatal_sick_leave_type_1")

		first_sick_leave_exists = frappe.db.exists("Leave Application", {"employee": self.employee_no,"leave_type": ["in",first_sick_leave_list],"docstatus": 1})
		first_fatal_sick_leave_exists = frappe.db.exists("Leave Application", {"employee": self.employee_no,"leave_type": first_fatal_sick_leave,"docstatus": 1})

		if self.leave_type in all_normal_sick_leave_list:
			if first_sick_leave_exists==None:
				frappe.db.set_value("Employee",self.employee_no,"custom_leave_cycle_start_date",None)
				frappe.db.set_value("Employee",self.employee_no,"custom_leave_cycle_end_date",None)
				frappe.msgprint(_("Leave Cycle Dates Cleared from Employee Record as no Sick Leave Applications exists"),alert=True)

		if self.leave_type in all_fatal_sick_leave_list:
			if first_fatal_sick_leave_exists==None:
				frappe.db.set_value("Employee",self.employee_no,"custom_fatal_leave_cycle_start_date",None)
				frappe.db.set_value("Employee",self.employee_no,"custom_fatal_leave_cycle_end_date",None)
				frappe.msgprint(_("Fatal Sick Leave Cycle Dates Cleared from Employee Record as no Fatal Sick Leave Applications exists"),alert=True)

	def validate_once_per_life_time_requests(self):
		if self.leave_type:
			is_once_per_lifetime = frappe.db.get_value("Leave Type", self.leave_type, "custom_once_in_company_life")
			if is_once_per_lifetime == 1:
				leave_request_exists = frappe.db.exists("Leave Request ST",
											{"employee_no": self.employee_no,"leave_type": self.leave_type,"name": ["!=",self.name]})
				if leave_request_exists:
					frappe.throw(_("Leave Type {0} is allowed only once in company life time".format(frappe.bold(self.leave_type))))

	def validate_from_to_dates(self):
		if self.from_date and self.to_date:
			if getdate(self.from_date) > getdate(self.to_date):
				frappe.throw(_("From Date cannot be greater than To Date"))
	
	def validate_future_dates(self):
		if self.from_date and self.to_date and self.leave_type:
			do_not_allow_future_dates = frappe.db.get_value("Leave Type", self.leave_type, "custom_dont_allow_future_date")
			if do_not_allow_future_dates == 1:
				if getdate(self.to_date) > getdate(today()):
					frappe.throw(_("Leave Type {0} does not allow future dates".format(frappe.bold(self.leave_type))))

	def validate_past_dates(self):
		if self.from_date and self.leave_type:
			max_allowed_days_to_apply_past_leave = frappe.db.get_value("Leave Type", self.leave_type, "custom_maximum_days_allowed_to_apply_past_date_leave")
			if max_allowed_days_to_apply_past_leave > 0:
				maximum_past_date_allowed = add_to_date(getdate(today()), days=-(max_allowed_days_to_apply_past_leave-1))
				if getdate(self.from_date) < getdate(maximum_past_date_allowed):
					frappe.throw(_("You are not allowed to apply leave for {0} from {1}.<br>You can apply leave from {2}".format(frappe.bold(self.leave_type), frappe.bold(self.from_date), frappe.bold(maximum_past_date_allowed))))
	
	def validate_attachments(self):
		print("validate_attachments-------------------------------")
		if self.leave_category==_("Sick"):
			if not self.attachment:
				frappe.throw(_("Attachment is mandatory for Sick Leave",frappe.MandatoryError))
				
		if self.leave_type:
			attachment_required = frappe.db.get_value("Leave Type", self.leave_type, "custom_attachment_required")
			if attachment_required == 1:
				if not self.attachment:
					frappe.throw(_("Attachment is mandatory for Leave Type <b>{0}</b>".format(self.leave_type)))

	def validate_deputy_employee_if_applicable(self):
		apply_deputy_for_manager = frappe.db.get_single_value("Stats Settings ST", "apply_deputy_for_manager")
		apply_deputy_for_employee = frappe.db.get_single_value("Stats Settings ST", "apply_deputy_for_employee")
		no_of_days_required_for_deputy = frappe.db.get_single_value("Stats Settings ST", "deputy_required_for_no_of_days_of_leave")
		is_applicable_for_deputy = self.is_manager
		if (is_applicable_for_deputy == 1 and is_applicable_for_deputy == apply_deputy_for_manager) or (is_applicable_for_deputy == 0 and is_applicable_for_deputy != apply_deputy_for_employee):
			if no_of_days_required_for_deputy:
				if cint(self.total_no_of_days) >= no_of_days_required_for_deputy:
					if self.deputy_employee == "" or self.deputy_employee == None:
						frappe.throw(_("Deputy Employee is mandatory when total no of days is greater than or equal to {0}".format(no_of_days_required_for_deputy)))
					else:
						deputy_employee_status = frappe.db.get_value("Employee", self.deputy_employee, "status")
						if deputy_employee_status != "Active":
							frappe.throw(_("Deputy Employee <b>{0}</b> is not active. Please select an active employee.".format(self.deputy_employee_name)))
						if self.deputy_employee == self.employee_no:
							frappe.throw(_("Deputy Employee cannot be the same as the employee applying for leave. Please select a different deputy employee."))
						else :
							validate_deputy_employee_not_apply_for_same_dates(self.from_date, self.to_date, self.deputy_employee)
			else:
				frappe.throw(_("Please set Deputy Required for No of Days of Leave in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))

	def calculate_to_date_based_on_no_of_days(self):
		print("calculate_to_date_based_on_no_of_days-------------------------------")
		to_date = add_to_date(getdate(self.from_date), days=self.total_no_of_days-1)

		include_holidays = frappe.db.get_value("Leave Type", self.leave_type, "include_holiday")
		final_to_date = getdate(to_date)

		# print(include_holidays, "=========include_holidays===")
		if include_holidays == 0:
			holidays = get_holidays(self.employee_no, self.from_date, final_to_date)
			if holidays > 0:
				while (holidays > 0):
					final_date = add_to_date(final_to_date, days=holidays)
					holidays = get_holidays(self.employee_no, add_to_date(final_to_date, days=1), final_date)
					final_to_date = final_date

		self.to_date = final_to_date
	
	def calculate_total_days_and_yearly_days(self):
		include_holidays = frappe.db.get_value("Leave Type", self.leave_type, "include_holiday")
		if self.from_date and self.to_date:
			if include_holidays == 1:
				# If holidays are included, we just calculate the total number of days
				total_no_of_days = date_diff(self.to_date, self.from_date) + 1
				# self.total_no_of_days = total_no_of_days
				from_date_year = getdate(self.from_date).year
				to_date_year = getdate(self.to_date).year
				if from_date_year == to_date_year:
					self.no_of_days_in_first_calendar_year = total_no_of_days
					self.no_of_days_in_second_calendar_year = 0
				else:
					first_year_last_date = getdate(f"{from_date_year}-12-31")
					first_year_days = date_diff(first_year_last_date, getdate(self.from_date))+1
					second_year_first_date = getdate(f"{to_date_year}-01-01")
					second_year_days = date_diff(getdate(self.to_date), second_year_first_date)+1
					self.no_of_days_in_first_calendar_year = first_year_days
					self.no_of_days_in_second_calendar_year = second_year_days
			else :
				# If holidays are not included, we need to check for holidays and calculate the total number of working days
				from_date_year = getdate(self.from_date).year
				to_date_year = getdate(self.to_date).year
				if from_date_year == to_date_year:
					total_no_of_days = self.get_no_of_days_based_on_holiday_list(self.from_date, self.to_date)

					# self.total_no_of_days = total_no_of_days
					self.no_of_days_in_first_calendar_year = self.total_no_of_days
					self.no_of_days_in_second_calendar_year = 0
					
				else:
					# Calculate first year days excluding holidays
					first_year_days, second_year_days = 0, 0
					first_year_last_date = getdate(f"{from_date_year}-12-31")
					first_year_days = self.get_no_of_days_based_on_holiday_list(self.from_date, first_year_last_date)

					# Calculate second year days excluding holidays
					second_year_first_date = getdate(f"{to_date_year}-01-01")
					second_year_days = self.get_no_of_days_based_on_holiday_list(second_year_first_date, self.to_date)

					# self.total_no_of_days = first_year_days + second_year_days
					self.no_of_days_in_first_calendar_year = first_year_days
					self.no_of_days_in_second_calendar_year = second_year_days

	def get_no_of_days_based_on_holiday_list(self, from_date, to_date):
		no_of_days = 0
		from_date_year = getdate(from_date).year
		holiday_list_exists = frappe.db.exists("Holiday List",
											{"from_date":["<=", from_date], "to_date":[">=", from_date]})
		if holiday_list_exists:
			actual_days = date_diff(to_date, from_date)+1
			holiday_count = 0
			for day in range(actual_days):
				current_date = add_to_date(from_date, days=day)
				if holiday_between_applied_dates(holiday_list_exists, current_date):
					holiday_count += 1
			no_of_days = actual_days - holiday_count
		else:
			frappe.throw(_("Holiday List for year <b>{0}</b> does not exists. Hence we cannot get holiday to ignore".format(from_date_year)))
		return no_of_days
			
	def validate_leave_type_with_no_of_days(self):
		if self.leave_type and self.total_no_of_days:
			max_leaves_allowed, max_continuous_days_allowed = frappe.db.get_value("Leave Type", self.leave_type, ["max_leaves_allowed","max_continuous_days_allowed"])
			new_baby_leave_type = frappe.db.get_single_value("Stats Settings ST", "new_baby_leave_type")
			if new_baby_leave_type and self.leave_type == new_baby_leave_type:
				if max_continuous_days_allowed < 1:
					frappe.throw(_("Please set Max Continuous Days Allowed for Leave Type {0}".format(get_link_to_form("Leave Type",self.leave_type))))
			if max_continuous_days_allowed and self.total_no_of_days > max_continuous_days_allowed:
				frappe.throw(_("Leave Type {0} has only {1} days allowed".format(frappe.bold(self.leave_type), frappe.bold(cint(max_continuous_days_allowed)))))
			elif max_leaves_allowed and self.total_no_of_days > max_leaves_allowed:
				frappe.throw(_("Leave Type {0} has only {1} days allowed".format(frappe.bold(self.leave_type), frappe.bold(cint(max_leaves_allowed)))))

	def validate_other_leave_consumed_days(self):
		print("validate_other_leave_consumed_days-------------------------------------")
		sick_leave_list = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_direct","sick_leave_type_2_direct","sick_leave_type_3_direct",
																				 "sick_leave_type_1_civil","sick_leave_type_2_civil","sick_leave_type_3_civil","sick_leave_type_4_civil",
																				 "fatal_sick_leave_type_1","fatal_sick_leave_type_2","fatal_sick_leave_type_3","fatal_sick_leave_type_4"])
		
		current_fiscal_year = get_fiscal_year(nowdate(), as_dict=True)
		if self.leave_type and self.leave_type not in sick_leave_list:
			self.check_remaining_leaves_of_allow_after_leave_type(current_fiscal_year.year_start_date, current_fiscal_year.year_end_date)
		else:
			fatal_sick_leave_type_list = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["fatal_sick_leave_type_1","fatal_sick_leave_type_2","fatal_sick_leave_type_3","fatal_sick_leave_type_4"])
			print("*"*100)
			print(self.to_date)
			if self.leave_type not in fatal_sick_leave_type_list:
				leave_year, leave_cycle_start_date, leave_cycle_end_date = is_leave_year_valid(self.from_date,self.to_date,self.employee_no)
				leave_dates_between_leave_cycle_year = is_leave_applied_dates_within_leave_cycle_year(self.from_date,self.to_date,self.employee_no,leave_type="Sick Leave")
			else:
				leave_year, leave_cycle_start_date, leave_cycle_end_date = is_fatal_leave_cycle_year_valid(self.from_date,self.to_date,self.employee_no)
				leave_dates_between_leave_cycle_year = is_leave_applied_dates_within_leave_cycle_year(self.from_date,self.to_date,self.employee_no,leave_type="Fatal Sick Leave")
			print(leave_year,"===========leave_year")
			if self.leave_type:
				if leave_year=="Exists":
					print("EEEEEEEEEEEE")
					if leave_dates_between_leave_cycle_year==True:
						print("YESSSSSSSSSS")
						self.check_remaining_leaves_of_allow_after_leave_type(leave_cycle_start_date, leave_cycle_end_date)
				elif leave_year=="Not Define" or leave_year=="Future Dates":
					print("NNNNNNNNNNNNNNNNNNNN")
					### If Leave Cycle Year is not
					if self.leave_type in sick_leave_list:
						allow_after_leave_type = frappe.db.get_value("Leave Type", self.leave_type, "custom_allow_after_consuming_balance_for")
						if allow_after_leave_type:
							frappe.throw(_("You cannot apply for <b>{0}</b>. <br>Because you have remaining leave balance of <b>{1}</b>.".format(self.leave_type,allow_after_leave_type)))
					# if self.leave_type==second_sick_leave:
					# 	allow_after_leave_type = frappe.db.get_value("Leave Type", second_sick_leave, "custom_allow_after_consuming_balance_for")
					# 	if allow_after_leave_type:
					# 		frappe.throw(_("You cannot apply for <b>{0}</b>. <br>Because you have remaining leave balance of <b>{1}</b>.".format(self.leave_type,allow_after_leave_type)))
					# if self.leave_type==third_sick_leave:
					# 	allow_after_leave_type = frappe.db.get_value("Leave Type", third_sick_leave, "custom_allow_after_consuming_balance_for")
					# 	if allow_after_leave_type:
					# 		frappe.throw(_("You cannot apply for <b>{0}</b>. <br>Because you have remaining leave balance of <b>{1}</b>.".format(self.leave_type,allow_after_leave_type)))

			# allow_after_leave_type = frappe.db.get_value("Leave Type", self.leave_type, "custom_allow_after_consuming_balance_for")
			# if allow_after_leave_type:
			# 	allow_after_leave_type_days = frappe.db.get_value("Leave Type", allow_after_leave_type, "max_leaves_allowed")
			# 	leave_application_for_allow_after_leave_type = frappe.db.get_all("Leave Application",
			# 														 filters={"docstatus": 1, "employee":self.employee_no,"leave_type":allow_after_leave_type,
			# 			   														"from_date": ["between", [current_fiscal_year.year_start_date, current_fiscal_year.year_end_date]],
			# 																	"to_date": ["between", [current_fiscal_year.year_start_date, current_fiscal_year.year_end_date]]},
			# 														 fields=["sum(total_leave_days) as total_leave_days"]) 
			# 	if leave_application_for_allow_after_leave_type:
			# 		leave_days_for_allow_after_leave_type = leave_application_for_allow_after_leave_type[0].total_leave_days
			# 		if leave_days_for_allow_after_leave_type==None:
			# 			leave_days_for_allow_after_leave_type = 0

			# 		leave_allocation_for_allow_after_leave_type = frappe.db.get_all("Leave Allocation",
			# 														filters={"docstatus": 1, "employee":self.employee_no,"leave_type":allow_after_leave_type,
			# 																"from_date": ["between", [current_fiscal_year.year_start_date, current_fiscal_year.year_end_date]],
			# 																"to_date": ["between", [current_fiscal_year.year_start_date, current_fiscal_year.year_end_date]]},
			# 														fields=["sum(total_leaves_allocated) as total_leaves_allocated"])
			# 		if leave_allocation_for_allow_after_leave_type:
			# 			allocated_days_for_allow_after_leave_type = leave_allocation_for_allow_after_leave_type[0].total_leaves_allocated
			# 			if allocated_days_for_allow_after_leave_type==None:
			# 				allocated_days_for_allow_after_leave_type = frappe.db.get_value("Leave Type", allow_after_leave_type, "max_leaves_allowed")

			# 		if flt(leave_days_for_allow_after_leave_type) < flt(allocated_days_for_allow_after_leave_type):
			# 			remaining_days_of_allow_after_leave_type = flt(allocated_days_for_allow_after_leave_type) - flt(leave_days_for_allow_after_leave_type)
			# 			print(remaining_days_of_allow_after_leave_type,"----------remaining_days_of_allow_after_leave_type")
			# 			if remaining_days_of_allow_after_leave_type > 1:
			# 				frappe.throw(_("You cannot apply for Leave Type {0} because {1} days of Leave Type {2} are remaining".format(
			# 					frappe.bold(self.leave_type), frappe.bold(flt(allocated_days_for_allow_after_leave_type) - flt(leave_days_for_allow_after_leave_type)), frappe.bold(allow_after_leave_type))))
	def check_remaining_leaves_of_allow_after_leave_type(self,leave_year_start_date, leave_year_end_date):
		allow_after_leave_type = frappe.db.get_value("Leave Type", self.leave_type, "custom_allow_after_consuming_balance_for")
		if allow_after_leave_type:
			# allow_after_leave_type_days = frappe.db.get_value("Leave Type", allow_after_leave_type, "max_leaves_allowed")
			leave_application_for_allow_after_leave_type = frappe.db.get_all("Leave Application",
																	filters={"docstatus": 1, "employee":self.employee_no,"leave_type":allow_after_leave_type,
																			"from_date": ["between", [leave_year_start_date, leave_year_end_date]],
																			"to_date": ["between", [leave_year_start_date, leave_year_end_date]]},
																	fields=["sum(total_leave_days) as total_leave_days"]) 
			if leave_application_for_allow_after_leave_type:
				leave_days_for_allow_after_leave_type = leave_application_for_allow_after_leave_type[0].total_leave_days
				if leave_days_for_allow_after_leave_type==None:
					leave_days_for_allow_after_leave_type = 0

				leave_allocation_for_allow_after_leave_type = frappe.db.get_all("Leave Allocation",
																filters={"docstatus": 1, "employee":self.employee_no,"leave_type":allow_after_leave_type,
																		"from_date": ["between", [leave_year_start_date, leave_year_end_date]],
																		"to_date": ["between", [leave_year_start_date, leave_year_end_date]]},
																fields=["sum(total_leaves_allocated) as total_leaves_allocated"])
				if leave_allocation_for_allow_after_leave_type:
					allocated_days_for_allow_after_leave_type = leave_allocation_for_allow_after_leave_type[0].total_leaves_allocated
					if allocated_days_for_allow_after_leave_type==None:
						allocated_days_for_allow_after_leave_type = frappe.db.get_value("Leave Type", allow_after_leave_type, "max_leaves_allowed")

				if flt(leave_days_for_allow_after_leave_type) < flt(allocated_days_for_allow_after_leave_type):
					remaining_days_of_allow_after_leave_type = flt(allocated_days_for_allow_after_leave_type) - flt(leave_days_for_allow_after_leave_type)
					print(remaining_days_of_allow_after_leave_type,"----------remaining_days_of_allow_after_leave_type")
					if remaining_days_of_allow_after_leave_type >= 1:
						frappe.throw(_("You cannot apply for Leave Type {0} because {1} days of Leave Type {2} are remaining".format(
							frappe.bold(self.leave_type), frappe.bold(flt(allocated_days_for_allow_after_leave_type) - flt(leave_days_for_allow_after_leave_type)), frappe.bold(allow_after_leave_type))))

	
	def create_leave_allocation_and_application_for_sick_leave_type(self):
		first_sick_leave_direct, first_sick_leave_civil, first_fatal_sick_leave = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_direct","sick_leave_type_1_civil","fatal_sick_leave_type_1"])
		civil_contract_years = frappe.db.get_single_value("Stats Settings ST", "leave_year_count_for_civil_contact_employees")
		fatal_sick_leave_years = frappe.db.get_single_value("Stats Settings ST", "leave_year_count_for_fatal_sick_leave")
		fatal_sick_leave_type_list = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["fatal_sick_leave_type_1","fatal_sick_leave_type_2","fatal_sick_leave_type_3","fatal_sick_leave_type_4"])
		if self.leave_type == first_sick_leave_direct or self.leave_type == first_sick_leave_civil or self.leave_type == first_fatal_sick_leave:
			if self.leave_type == first_fatal_sick_leave:
				leave_year, leave_cycle_start_date, leave_cycle_end_date = is_fatal_leave_cycle_year_valid(self.from_date,self.to_date,self.employee_no)
			else:
				leave_year, leave_cycle_start_date, leave_cycle_end_date = is_leave_year_valid(self.from_date,self.to_date,self.employee_no)
			print(leave_year,"===========leave_year")
			if leave_year=="Not Define":

				### Define Leave Cycle Year Start/End Date based on Contract Type
				### If Contract Type is Direct then Leave Cycle Year is from From Date to next 12 months
				### If Contract Type is Civil then Leave Cycle Year is from From Date to 4 years ( years will be set in Stats Settings ST)
				if self.leave_type not in fatal_sick_leave_type_list:
					if _(self.contract_type) == _("Direct"):
						leave_cycle_year_start_date = self.from_date
						leave_cycle_year_end_date = add_to_date(add_months(self.from_date, 12),days=-1)
						print(leave_cycle_year_end_date,"===========direct year==================")
					elif _(self.contract_type) == _("Civil"):
						if civil_contract_years and civil_contract_years > 0:
							print("CCCCCCCCCCCCCC")
							leave_cycle_year_start_date = self.from_date
							leave_cycle_year_end_date = add_to_date(add_months(self.from_date, civil_contract_years*12),days=-1)
							print(leave_cycle_year_end_date,"===========civil year==================")
						else:
							frappe.throw(_("Please set <b>Leave Year Count For Civil Contact Employees</b> in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
				else:
					if fatal_sick_leave_years and fatal_sick_leave_years > 0:
						leave_cycle_year_start_date = self.from_date
						leave_cycle_year_end_date = add_to_date(add_months(self.from_date, fatal_sick_leave_years*12),days=-1)
						print(leave_cycle_year_end_date,"===========fatal year==================")
					else:
						frappe.throw(_("Please set <b>Leave Year Count For Fatal Sick Leave</b> in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
				print(leave_cycle_year_start_date,"===========leave_cycle_year_start_date",leave_cycle_year_end_date)
				print(self.from_date, self.to_date,"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
				### Create Leave Allocation for all Sick Leave Types

				self.create_leave_allocation_for_all_sick_leave_type(leave_cycle_year_start_date, leave_cycle_year_end_date)

				### Update Leave Cycle Start/End Date in Employee Profile
				if self.leave_type not in fatal_sick_leave_type_list:
					self.set_leave_cycle_year_in_employee_profile(leave_cycle_year_start_date, leave_cycle_year_end_date,leave_type="Sick Leave")
				else:
					self.set_leave_cycle_year_in_employee_profile(leave_cycle_year_start_date, leave_cycle_year_end_date,leave_type="Fatal Sick Leave")
			
			if leave_year=="Future Dates":
				if getdate(self.from_date) > leave_cycle_end_date:
					if self.leave_type not in fatal_sick_leave_type_list:
						if _(self.contract_type) == _("Direct"):
							new_leave_cycle_year_start_date = self.from_date
							new_leave_cycle_year_end_date = add_to_date(add_months(self.from_date, 12),days=-1)
						elif _(self.contract_type) == _("Civil"):
							if civil_contract_years and civil_contract_years > 0:
								new_leave_cycle_year_start_date = self.from_date
								new_leave_cycle_year_end_date = add_to_date(add_months(self.from_date, civil_contract_years*12),days=-1)
							else:
								frappe.throw(_("Please set <b>Leave Year Count For Civil Contact Employees</b> in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
						self.set_leave_cycle_year_in_employee_profile(new_leave_cycle_year_start_date, new_leave_cycle_year_end_date,leave_type="Sick Leave")
					else:
						if fatal_sick_leave_years and fatal_sick_leave_years > 0:
							new_leave_cycle_year_start_date = self.from_date
							new_leave_cycle_year_end_date = add_to_date(add_months(self.from_date, fatal_sick_leave_years*12),days=-1)
						else:
							frappe.throw(_("Please set <b>Leave Year Count For Fatal Sick Leave</b> in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
						self.set_leave_cycle_year_in_employee_profile(new_leave_cycle_year_start_date, new_leave_cycle_year_end_date,leave_type="Fatal Sick Leave")

					self.create_leave_allocation_for_all_sick_leave_type(new_leave_cycle_year_start_date, new_leave_cycle_year_end_date)

		self.create_leave_application(self.from_date, self.to_date, self.total_no_of_days)

	def create_leave_allocation_for_all_sick_leave_type(self,leave_cycle_year_start_date, leave_cycle_year_end_date):

		fatal_sick_leave_type_list = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["fatal_sick_leave_type_1","fatal_sick_leave_type_2","fatal_sick_leave_type_3","fatal_sick_leave_type_4"])

		if self.leave_type not in fatal_sick_leave_type_list:
		
			if _(self.contract_type) == _("Direct"):
				first_sick_leave, second_sick_leave, third_sick_leave = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_direct","sick_leave_type_2_direct","sick_leave_type_3_direct"])
				leave_allocation_exists_for_first_sick_leave_type, leave_allocation_reference_of_first_sick_leave_type = leave_allocation_exists_for_leave_cycle_year(leave_cycle_year_start_date, leave_cycle_year_end_date, self.employee_no, first_sick_leave)
				if leave_allocation_exists_for_first_sick_leave_type==False:
					max_allowed_days = frappe.db.get_value("Leave Type",first_sick_leave,"max_leaves_allowed")
					self.create_leave_allocation(leave_cycle_year_start_date, leave_cycle_year_end_date, max_allowed_days, first_sick_leave)
				leave_allocation_exists_for_second_sick_leave_type, leave_allocation_reference_of_second_sick_leave_type = leave_allocation_exists_for_leave_cycle_year(leave_cycle_year_start_date, leave_cycle_year_end_date, self.employee_no, second_sick_leave)
				if leave_allocation_exists_for_second_sick_leave_type==False:
					max_allowed_days = frappe.db.get_value("Leave Type",second_sick_leave,"max_leaves_allowed")
					self.create_leave_allocation(leave_cycle_year_start_date, leave_cycle_year_end_date, max_allowed_days, second_sick_leave)
				leave_allocation_exists_for_third_sick_leave_type, leave_allocation_reference_of_third_sick_leave_type = leave_allocation_exists_for_leave_cycle_year(leave_cycle_year_start_date, leave_cycle_year_end_date, self.employee_no, third_sick_leave)
				if leave_allocation_exists_for_third_sick_leave_type==False:
					max_allowed_days = frappe.db.get_value("Leave Type",third_sick_leave,"max_leaves_allowed")
					self.create_leave_allocation(leave_cycle_year_start_date, leave_cycle_year_end_date, max_allowed_days, third_sick_leave)

			elif _(self.contract_type) == _("Civil"):
				first_sick_leave, second_sick_leave, third_sick_leave, fourth_sick_leave = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_civil","sick_leave_type_2_civil","sick_leave_type_3_civil","sick_leave_type_4_civil"])
				leave_allocation_exists_for_first_sick_leave_type, leave_allocation_reference_of_first_sick_leave_type = leave_allocation_exists_for_leave_cycle_year(leave_cycle_year_start_date, leave_cycle_year_end_date, self.employee_no, first_sick_leave)
				if leave_allocation_exists_for_first_sick_leave_type==False:
					max_allowed_days = frappe.db.get_value("Leave Type",first_sick_leave,"max_leaves_allowed")
					self.create_leave_allocation(leave_cycle_year_start_date, leave_cycle_year_end_date, max_allowed_days, first_sick_leave)
				leave_allocation_exists_for_second_sick_leave_type, leave_allocation_reference_of_second_sick_leave_type = leave_allocation_exists_for_leave_cycle_year(leave_cycle_year_start_date, leave_cycle_year_end_date, self.employee_no, second_sick_leave)
				if leave_allocation_exists_for_second_sick_leave_type==False:
					max_allowed_days = frappe.db.get_value("Leave Type",second_sick_leave,"max_leaves_allowed")
					self.create_leave_allocation(leave_cycle_year_start_date, leave_cycle_year_end_date, max_allowed_days, second_sick_leave)
				leave_allocation_exists_for_third_sick_leave_type, leave_allocation_reference_of_third_sick_leave_type = leave_allocation_exists_for_leave_cycle_year(leave_cycle_year_start_date, leave_cycle_year_end_date, self.employee_no, third_sick_leave)
				if leave_allocation_exists_for_third_sick_leave_type==False:
					max_allowed_days = frappe.db.get_value("Leave Type",third_sick_leave,"max_leaves_allowed")
					self.create_leave_allocation(leave_cycle_year_start_date, leave_cycle_year_end_date, max_allowed_days, third_sick_leave)
				leave_allocation_exists_for_fourth_sick_leave_type, leave_allocation_reference_of_fourth_sick_leave_type = leave_allocation_exists_for_leave_cycle_year(leave_cycle_year_start_date, leave_cycle_year_end_date, self.employee_no, fourth_sick_leave)
				if leave_allocation_exists_for_fourth_sick_leave_type==False:
					max_allowed_days = frappe.db.get_value("Leave Type",fourth_sick_leave,"max_leaves_allowed")
					self.create_leave_allocation(leave_cycle_year_start_date, leave_cycle_year_end_date, max_allowed_days, fourth_sick_leave)
		else:
			### Create Leave Allocation for all Fatal Sick Leave Types
			first_fatal_sick_leave, second_fatal_sick_leave, third_fatal_sick_leave, fourth_fatal_sick_leave = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["fatal_sick_leave_type_1","fatal_sick_leave_type_2","fatal_sick_leave_type_3","fatal_sick_leave_type_4"])
			if self.leave_type in [first_fatal_sick_leave, second_fatal_sick_leave, third_fatal_sick_leave, fourth_fatal_sick_leave]:
				leave_allocation_exists_for_first_fatal_sick_leave_type, leave_allocation_reference_of_first_fatal_sick_leave_type = leave_allocation_exists_for_leave_cycle_year(leave_cycle_year_start_date, leave_cycle_year_end_date, self.employee_no, first_fatal_sick_leave)
				if leave_allocation_exists_for_first_fatal_sick_leave_type==False:
					max_allowed_days = frappe.db.get_value("Leave Type",first_fatal_sick_leave,"max_leaves_allowed")
					self.create_leave_allocation(leave_cycle_year_start_date, leave_cycle_year_end_date, max_allowed_days, first_fatal_sick_leave)
				leave_allocation_exists_for_second_fatal_sick_leave_type, leave_allocation_reference_of_second_fatal_sick_leave_type = leave_allocation_exists_for_leave_cycle_year(leave_cycle_year_start_date, leave_cycle_year_end_date, self.employee_no, second_fatal_sick_leave)
				if leave_allocation_exists_for_second_fatal_sick_leave_type==False:
					max_allowed_days = frappe.db.get_value("Leave Type",second_fatal_sick_leave,"max_leaves_allowed")
					self.create_leave_allocation(leave_cycle_year_start_date, leave_cycle_year_end_date, max_allowed_days, second_fatal_sick_leave)
				leave_allocation_exists_for_third_fatal_sick_leave_type, leave_allocation_reference_of_third_fatal_sick_leave_type = leave_allocation_exists_for_leave_cycle_year(leave_cycle_year_start_date, leave_cycle_year_end_date, self.employee_no, third_fatal_sick_leave)
				if leave_allocation_exists_for_third_fatal_sick_leave_type==False:
					max_allowed_days = frappe.db.get_value("Leave Type",third_fatal_sick_leave,"max_leaves_allowed")
					self.create_leave_allocation(leave_cycle_year_start_date, leave_cycle_year_end_date, max_allowed_days, third_fatal_sick_leave)
				leave_allocation_exists_for_fourth_fatal_sick_leave_type, leave_allocation_reference_of_fourth_fatal_sick_leave_type = leave_allocation_exists_for_leave_cycle_year(leave_cycle_year_start_date, leave_cycle_year_end_date, self.employee_no, fourth_fatal_sick_leave)
				if leave_allocation_exists_for_fourth_fatal_sick_leave_type==False:
					max_allowed_days = frappe.db.get_value("Leave Type",fourth_fatal_sick_leave,"max_leaves_allowed")
					self.create_leave_allocation(leave_cycle_year_start_date, leave_cycle_year_end_date, max_allowed_days, fourth_fatal_sick_leave)

	def set_leave_cycle_year_in_employee_profile(self, leave_cycle_year_start_date, leave_cycle_year_end_date,leave_type=None):
		employee_doc = frappe.get_doc("Employee",self.employee_no)
		if leave_type == "Sick Leave":
			employee_doc.custom_leave_cycle_start_date=leave_cycle_year_start_date
			employee_doc.custom_leave_cycle_end_date=leave_cycle_year_end_date
			employee_doc.add_comment("Comment",_("Leave Cycle Start Date and Leave Cycle End Date are updated due to {0}".format(get_link_to_form("Leave Request ST",self.name))))
		elif leave_type == "Fatal Sick Leave":
			employee_doc.custom_fatal_leave_cycle_start_date=leave_cycle_year_start_date
			employee_doc.custom_fatal_leave_cycle_end_date=leave_cycle_year_end_date
			employee_doc.add_comment("Comment",_("Fatal Leave Cycle Start Date and Fatal Leave Cycle End Date are updated due to {0}".format(get_link_to_form("Leave Request ST",self.name))))
		employee_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Leave Cycle Year is Updated in Employee {0}".format(get_link_to_form("Employee",self.employee_no))),alert=True)

	def create_leave_allocation_and_application_based_on_days_per_year(self):
		if self.total_no_of_days:
			current_year_start_date = getdate(f"{getdate(self.from_date).year}-01-01")
			current_year_end_date = getdate(f"{getdate(self.from_date).year}-12-31")
			if self.no_of_days_in_second_calendar_year == 0:
				leave_allocation_exists_for_same_leave_type = frappe.db.exists("Leave Allocation",
					{"docstatus":1,"employee": self.employee_no, "leave_type": self.leave_type, "from_date":["between", [current_year_start_date, current_year_end_date]], "to_date":["between", [current_year_start_date,current_year_end_date]]})
				if leave_allocation_exists_for_same_leave_type:
					previous_allocation_doc = frappe.get_doc("Leave Allocation", leave_allocation_exists_for_same_leave_type)
					previous_allocation_doc.new_leaves_allocated = previous_allocation_doc.new_leaves_allocated + self.total_no_of_days
					previous_allocation_doc.add_comment("Comment", text=_("Leave Allocation is updated due to Leave Request ST {0}".format(get_link_to_form("Leave Request ST",self.name))))
					previous_allocation_doc.save(ignore_permissions=True)
					frappe.msgprint(_("Leave Allocation is updated for year <b>{0}</b>".format((current_year_start_date).year)),alert=True)
				else:
					is_lwp = frappe.db.get_value("Leave Type", self.leave_type, "is_lwp")
					if is_lwp == 0:
						self.create_leave_allocation(current_year_start_date, current_year_end_date, self.total_no_of_days, self.leave_type)
				self.create_leave_application(self.from_date, self.to_date, self.total_no_of_days)
			elif self.no_of_days_in_second_calendar_year > 0:
				leave_allocation_exists_for_same_leave_type = frappe.db.exists("Leave Allocation",
					{"docstatus":1,"employee": self.employee_no, "leave_type": self.leave_type, "from_date":["between", [current_year_start_date, current_year_end_date]], "to_date":["between", [current_year_start_date,current_year_end_date]]})
				if leave_allocation_exists_for_same_leave_type:
					previous_allocation_doc = frappe.get_doc("Leave Allocation", leave_allocation_exists_for_same_leave_type)
					previous_allocation_doc.new_leaves_allocated = previous_allocation_doc.new_leaves_allocated + self.no_of_days_in_first_calendar_year
					previous_allocation_doc.add_comment("Comment", text=_("Leave Allocation is updated due to Leave Request ST {0}".format(get_link_to_form("Leave Request ST",self.name))))
					previous_allocation_doc.save(ignore_permissions=True)
					frappe.msgprint(_("Leave Allocation is updated for year <b>{0}</b>".format((current_year_start_date).year)),alert=True)
				else:
					is_lwp = frappe.db.get_value("Leave Type", self.leave_type, "is_lwp")
					if is_lwp == 0:
						self.create_leave_allocation(current_year_start_date, current_year_end_date, self.no_of_days_in_first_calendar_year, self.leave_type)
				self.create_leave_application(self.from_date, current_year_end_date, self.no_of_days_in_first_calendar_year)
				next_year_start_date = getdate(f"{getdate(self.to_date).year}-01-01")
				next_year_end_date = getdate(f"{getdate(self.to_date).year}-12-31")
				leave_allocation_exists_for_same_leave_type = frappe.db.exists("Leave Allocation",
					{"docstatus":1,"employee": self.employee_no, "leave_type": self.leave_type, "from_date":["between", [next_year_start_date, next_year_end_date]], "to_date":["between", [next_year_start_date,next_year_end_date]]})
				if leave_allocation_exists_for_same_leave_type:
					previous_allocation_doc = frappe.get_doc("Leave Allocation", leave_allocation_exists_for_same_leave_type)
					previous_allocation_doc.new_leaves_allocated = previous_allocation_doc.new_leaves_allocated + self.no_of_days_in_second_calendar_year
					previous_allocation_doc.add_comment("Comment", text=_("Leave Allocation is updated due to Leave Request ST {0}".format(get_link_to_form("Leave Request ST",self.name))))
					previous_allocation_doc.save(ignore_permissions=True)
					frappe.msgprint(_("Leave Allocation is updated for year <b>{0}</b>".format((next_year_start_date).year)),alert=True)
				else:
					is_lwp = frappe.db.get_value("Leave Type", self.leave_type, "is_lwp")
					if is_lwp == 0:
						self.create_leave_allocation(next_year_start_date, next_year_end_date, self.no_of_days_in_second_calendar_year, self.leave_type)
				self.create_leave_application(next_year_start_date, self.to_date, self.no_of_days_in_second_calendar_year)
				
	def create_leave_allocation(self, from_date, to_date, no_of_days, leave_type):
		leave_allocation_doc = frappe.new_doc("Leave Allocation")
		leave_allocation_doc.employee = self.employee_no
		leave_allocation_doc.leave_type = leave_type
		leave_allocation_doc.from_date = from_date
		leave_allocation_doc.to_date = to_date
		leave_allocation_doc.new_leaves_allocated = no_of_days
		leave_allocation_doc.custom_leave_request_reference = self.name
		leave_allocation_doc.save(ignore_permissions=True)
		leave_allocation_doc.submit()
		frappe.msgprint(_("Leave Allocation <b>{0}</b> is Created for employee <b>{1}</b> for Leave Type <b>{2}</b>".format(get_link_to_form("Leave Allocation",leave_allocation_doc.name),self.employee_no,self.leave_type)),alert=True)

	def create_leave_application(self, from_date, to_date, no_of_days):
		leave_application_doc = frappe.new_doc("Leave Application")
		leave_application_doc.employee = self.employee_no
		leave_application_doc.leave_type = self.leave_type
		leave_application_doc.from_date = from_date
		leave_application_doc.to_date = to_date
		leave_application_doc.total_leave_days = no_of_days
		leave_application_doc.posting_date = today()
		leave_application_doc.custom_leave_request_reference = self.name
		leave_application_doc.custom_deputy_employee = self.deputy_employee
		leave_application_doc.custom_deputy_employee_name = self.deputy_employee_name
		leave_application_doc.save(ignore_permissions=True)
		leave_application_doc.submit()
		frappe.msgprint(_("Leave Application <b>{0}</b> is created".format(get_link_to_form("Leave Application",leave_application_doc.name))),alert=True)

	@frappe.whitelist()
	def create_leave_request_for_baby_medical_and_extended_vacation(self, leave_type):
		leave_request_doc = frappe.new_doc("Leave Request ST")
		leave_request_doc.employee_no = self.employee_no

		if leave_type == "Medical":
			baby_health_leave_type = frappe.db.get_single_value("Stats Settings ST", "baby_health_leave_type")
			if baby_health_leave_type:
				leave_request_doc.leave_type = baby_health_leave_type
			else:
				frappe.throw(_("Please set Baby Health Leave Type in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
		elif leave_type == "Extended":
			baby_extended_leave_type = frappe.db.get_single_value("Stats Settings ST", "baby_extended_leave_type")
			if baby_extended_leave_type:
				leave_request_doc.leave_type = baby_extended_leave_type
			else:
				frappe.throw(_("Please set Baby Extended Leave Type in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
		
		leave_request_doc.from_date = add_to_date(self.to_date, days=1)
		leave_request_doc.leave_request_reference = self.name
		leave_request_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Leave Request for Baby {0} Leave is created <b>{1}</b>".format(leave_type,get_link_to_form("Leave Request ST",leave_request_doc.name))),alert=True)
		return leave_request_doc.name

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_leave_type(doctype, txt, searchfield, start, page_len, filters):
	gender = filters.get("gender")
	religion = filters.get("religion")
	contract_type = filters.get("contract_type")
	marital_status = filters.get("marital_status")
	employee = filters.get("employee")
	leave_category = filters.get("leave_category")

	baby_extended_leave_type, baby_health_leave_type = frappe.db.get_value("Stats Settings ST","Stats Settings ST", ["baby_extended_leave_type", "baby_health_leave_type"])

	leave_type = frappe.get_all("Leave Type", fields=["name","custom_is_applicable_for_gender_type", "custom_gender","custom_religion", "custom_is_applicable_for_contract_type","custom_contract_type", "custom_allow_leave_for_marital_status", "custom_marital_status"], filters={"name": ("like", f"{txt}%")},
							 or_filters = [["custom_once_in_company_life" , "=" , 1], ["custom_based_on_leave_request", "=", 1]])
	
	leave_type_list = []
	for l in leave_type:
		leave_type_list.append(l.name)

	for leave in leave_type:
		if leave.name == baby_extended_leave_type or leave.name == baby_health_leave_type:
			leave_type_list.remove(leave.name)
			
		elif leave.custom_is_applicable_for_gender_type == 1 and leave.custom_gender == gender and leave.custom_allow_leave_for_marital_status == 1 and leave.custom_marital_status != marital_status:
			leave_type_list.remove(leave.name)
			
		elif leave.custom_is_applicable_for_gender_type == 1 and leave.custom_gender != gender:
			leave_type_list.remove(leave.name)
			
		elif leave.custom_is_applicable_for_religion == 1 and (religion == None or religion == "") and leave.custom_religion:
			leave_type_list.remove(leave.name)
			
		elif leave.custom_is_applicable_for_religion == 1 and religion and leave.custom_religion and (religion != leave.custom_religion):
			leave_type_list.remove(leave.name)
			
		elif (leave.custom_is_applicable_for_contract_type == 1) and (leave.custom_contract_type != contract_type):
			leave_type_list.remove(leave.name)
	
	first_sick_leave_direct, first_sick_leave_civil, first_fatal_sick_leave = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_direct","sick_leave_type_1_civil","fatal_sick_leave_type_1"])

	sick_leave_cycle_start_date, sick_leave_cycle_end_date = frappe.db.get_value("Employee",employee,["custom_leave_cycle_start_date","custom_leave_cycle_end_date"])
	fatal_sick_leave_cycle_start_date, fatal_sick_leave_cycle_end_date = frappe.db.get_value("Employee",employee,["custom_fatal_leave_cycle_start_date","custom_fatal_leave_cycle_end_date"])

	first_sick_leave, second_sick_leave, third_sick_leave = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_direct","sick_leave_type_2_direct","sick_leave_type_3_direct"])
	if sick_leave_cycle_start_date and sick_leave_cycle_end_date:
		leave_application_list = frappe.db.get_all("Leave Application",
											filters={"docstatus":1,"status":"Approved","leave_type":first_sick_leave_direct,"employee":employee,"from_date":["between",[sick_leave_cycle_start_date,sick_leave_cycle_end_date]],"to_date":["between",[sick_leave_cycle_start_date,sick_leave_cycle_end_date]]},
											fields=["name"])
		if len(leave_application_list)==0:
			if second_sick_leave in leave_type_list:
				leave_type_list.remove(second_sick_leave)
			if third_sick_leave in leave_type_list:
				leave_type_list.remove(third_sick_leave)
	else:
		if second_sick_leave in leave_type_list:
			leave_type_list.remove(second_sick_leave)
		if third_sick_leave in leave_type_list:
			leave_type_list.remove(third_sick_leave)
	
	first_sick_leave_civil, second_sick_leave_civil, third_sick_leave_civil, fourth_sick_leave_civil = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_civil","sick_leave_type_2_civil","sick_leave_type_3_civil","sick_leave_type_4_civil"])
	# if sick_leave_cycle_start_date and sick_leave_cycle_end_date:
	# 	leave_application_list = frappe.db.get_all("Leave Application",
	# 										filters={"docstatus":1,"status":"Approved","leave_type":first_sick_leave_civil,"employee":employee,"from_date":["between",[sick_leave_cycle_start_date,sick_leave_cycle_end_date]],"to_date":["between",[sick_leave_cycle_start_date,sick_leave_cycle_end_date]]},
	# 										fields=["name"])
	# 	print(leave_application_list,"======")
	# 	if len(leave_application_list)==0:
	# 		if second_sick_leave in leave_type_list:
	# 			leave_type_list.remove(second_sick_leave)
	# 		if third_sick_leave in leave_type_list:
	# 			leave_type_list.remove(third_sick_leave)
	# 		if fourth_sick_leave in leave_type_list:
	# 			leave_type_list.remove(fourth_sick_leave)
	# else:
	# 	if second_sick_leave in leave_type_list:
	# 		leave_type_list.remove(second_sick_leave)
	# 	if third_sick_leave in leave_type_list:
	# 		leave_type_list.remove(third_sick_leave)
	# 	if fourth_sick_leave in leave_type_list:
	# 		leave_type_list.remove(fourth_sick_leave)
	
	first_sick_leave_fatal, second_sick_leave_fatal, third_sick_leave_fatal, fourth_sick_leave_fatal = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["fatal_sick_leave_type_1","fatal_sick_leave_type_2","fatal_sick_leave_type_3","fatal_sick_leave_type_4"])
	# if fatal_sick_leave_cycle_start_date and fatal_sick_leave_cycle_end_date:
	# 	leave_application_list = frappe.db.get_all("Leave Application",
	# 										filters={"docstatus":1,"status":"Approved","leave_type":first_fatal_sick_leave,"employee":employee,"from_date":["between",[fatal_sick_leave_cycle_start_date,sick_leave_cycle_end_date]],"to_date":["between",[fatal_sick_leave_cycle_start_date,fatal_sick_leave_cycle_end_date]]},
	# 										fields=["name"])
	# 	if len(leave_application_list)==0:
	# 		if second_sick_leave in leave_type_list:
	# 			leave_type_list.remove(second_sick_leave)
	# 		if third_sick_leave in leave_type_list:
	# 			leave_type_list.remove(third_sick_leave)
	# 		if fourth_sick_leave in leave_type_list:
	# 			leave_type_list.remove(fourth_sick_leave)
	# else:
	# 	if second_sick_leave in leave_type_list:
	# 		leave_type_list.remove(second_sick_leave)
	# 	if third_sick_leave in leave_type_list:
	# 		leave_type_list.remove(third_sick_leave)
	# 	if fourth_sick_leave in leave_type_list:
	# 		leave_type_list.remove(fourth_sick_leave)

	civil_type_leaves = [ first_sick_leave_civil, second_sick_leave_civil, third_sick_leave_civil, fourth_sick_leave_civil, 
					  first_sick_leave_fatal, second_sick_leave_fatal, third_sick_leave_fatal, fourth_sick_leave_fatal]

	if contract_type == "Civil":
		if leave_category == "Sick":
			leave_type_list = []
			leave_type_list = civil_type_leaves
		else:
			for civil_leave in civil_type_leaves:
				if civil_leave in leave_type_list:
					leave_type_list.remove(civil_leave)

	unique = tuple((i,) for i in leave_type_list)
	return unique

@frappe.whitelist()
def open_leave_request_for_baby_medical_vacation(source_name, target_doc=None):
	doc = frappe.get_doc("Leave Request ST", source_name)
	def set_missing_values(source, target):
		
		target.from_date = add_to_date(doc.to_date, days=1)
		baby_health_leave_type = frappe.db.get_single_value("Stats Settings ST", "baby_health_leave_type")
		if baby_health_leave_type:
			target.leave_type = baby_health_leave_type
		else:
			frappe.throw(_("Please set Baby Health Leave Type in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
		
		target.employee_no = doc.employee_no
		target.to_date = ""
		target.total_no_of_days = 0
		target.no_of_days_in_first_calendar_year = 0
		target.no_of_days_in_second_calendar_year = 0
		target.leave_request_reference = doc.name

	doc = get_mapped_doc(
		"Leave Request ST",
		source_name,
		{
			"Leave Request ST": {
				"doctype": "Leave Request ST",
			}
		},
		target_doc,
		set_missing_values,
	)

	return doc

@frappe.whitelist()
def open_leave_request_for_baby_extended_vacation(source_name, target_doc=None):
	doc = frappe.get_doc("Leave Request ST", source_name)
	def set_missing_values(source, target):
		
		target.from_date = add_to_date(doc.to_date, days=1)
		baby_extended_leave_type = frappe.db.get_single_value("Stats Settings ST", "baby_extended_leave_type")
		if baby_extended_leave_type:
			target.leave_type = baby_extended_leave_type
		else:
			frappe.throw(_("Please set Baby Extended Leave Type in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
		
		target.employee_no = doc.employee_no
		target.to_date = ""
		target.total_no_of_days = 0
		target.no_of_days_in_first_calendar_year = 0
		target.no_of_days_in_second_calendar_year = 0
		target.leave_request_reference = doc.name

	doc = get_mapped_doc(
		"Leave Request ST",
		source_name,
		{
			"Leave Request ST": {
				"doctype": "Leave Request ST"
			}
		},
		target_doc,
		set_missing_values,
	)

	return doc

@frappe.whitelist()
def create_leave_request_for_baby_extended_vacation_from_medical(source_name, target_doc=None):
	doc = frappe.get_doc("Leave Request ST", source_name)
	def set_missing_values(source, target):
		
		target.from_date = add_to_date(doc.to_date, days=1)
		baby_extended_leave_type = frappe.db.get_single_value("Stats Settings ST", "baby_extended_leave_type")
		if baby_extended_leave_type:
			target.leave_type = baby_extended_leave_type
		else:
			frappe.throw(_("Please set Baby Extended Leave Type in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
		
		target.employee_no = doc.employee_no
		target.to_date = ""
		target.total_no_of_days = 0
		target.no_of_days_in_first_calendar_year = 0
		target.no_of_days_in_second_calendar_year = 0
		target.leave_request_reference = doc.name

	doc = get_mapped_doc(
		"Leave Request ST",
		source_name,
		{
			"Leave Request ST": {
				"doctype": "Leave Request ST"
			}
		},
		target_doc,
		set_missing_values,
	)

	return doc

@frappe.whitelist()
def get_leave_details(employee, date, leave_type, for_salary_slip=False):
	sick_leave_types = frappe.db.get_value("Stats Settings ST","Stats Settings ST",["sick_leave_type_1_direct","sick_leave_type_2_direct","sick_leave_type_3_direct",
																				 "sick_leave_type_1_civil","sick_leave_type_2_civil","sick_leave_type_3_civil","sick_leave_type_4_civil",
																				 "fatal_sick_leave_type_1","fatal_sick_leave_type_2","fatal_sick_leave_type_3","fatal_sick_leave_type_4"])
	print(sick_leave_types,"======sick_leave_types")
	allocation_records = get_leave_allocation_records(employee, date)
	print(allocation_records,"===========allocation_records")
	leave_allocation = {}
	precision = cint(frappe.db.get_single_value("System Settings", "float_precision")) or 2

	for d in allocation_records:
		print(d,"d")
		if len(sick_leave_types)>0:
			if d in sick_leave_types:
				print(d,"===d=====")
				allocation = allocation_records.get(d, frappe._dict())
				to_date = date if for_salary_slip else allocation.to_date
				remaining_leaves = get_leave_balance_on(
					employee,
					d,
					date,
					to_date=to_date,
					consider_all_leaves_in_the_allocation_period=False if for_salary_slip else True,
				)

				leaves_taken = get_leaves_for_period(employee, d, allocation.from_date, to_date) * -1
				# leaves_pending = get_leaves_pending_approval_for_period(employee, d, allocation.from_date, to_date)
				# expired_leaves = allocation.total_leaves_allocated - (remaining_leaves + leaves_taken)

				leave_allocation[d] = {
					"total_leaves": flt(allocation.total_leaves_allocated, precision),
					# "expired_leaves": flt(expired_leaves, precision) if expired_leaves > 0 else 0,
					"leaves_taken": flt(leaves_taken, precision),
					# "leaves_pending_approval": flt(leaves_pending, precision),
					"remaining_leaves": flt(remaining_leaves, precision),
				}

	return {
		"leave_allocation": leave_allocation,
		"current_leave_type": leave_type,
		"leave_types_list": sick_leave_types
	}
