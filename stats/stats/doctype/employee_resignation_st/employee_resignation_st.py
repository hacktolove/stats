# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_to_date, cint
from stats.salary import get_latest_salary_structure_assignment

class EmployeeResignationST(Document):
	def validate(self):
		self.validate_resignation_date()
		# self.set_relieving_date_in_employee()

	def on_submit(self):
		self.set_relieving_date_in_employee()

	def validate_resignation_date(self):
		ignore_last_working_days = frappe.db.get_single_value('Stats Settings ST', 'ignore_last_working_date')

		if self.last_working_days and ignore_last_working_days == 0:
			today_month = getdate(nowdate()).month
			today_year = getdate(nowdate()).year
			resignation_month = getdate(self.last_working_days).month
			resignation_year = getdate(self.last_working_days).year

			if (today_month == resignation_month) and (today_year == resignation_year):

				payroll_date = frappe.db.get_single_value('Stats Settings ST', 'every_month_payroll_date')

				if payroll_date == None:
					frappe.throw(_("Please Set Every Month Payroll Date In Stats Settings."))
				# today_date = nowdate().day
				last_working_days = getdate(self.last_working_days).day

				if last_working_days < cint(payroll_date):
					print("start before payroll")
				elif last_working_days >= cint(payroll_date):
					print("start after payroll")
					frappe.throw(_("For this Month, Payroll is generated so you cannot apply for resignation"))
				else:
					pass					

			# Last Working day should not be less than notic period
			notice_period_days = frappe.db.get_value("Employee", self.employee_no, 'notice_number_of_days')
			joining_date = frappe.db.get_value("Employee", self.employee_no, 'date_of_joining')
			# test_period = add_to_date(getdate(joining_date), months=6)

			if not notice_period_days:
				frappe.throw(_("Please Set Notice Period Days in Employee Profile."))
			# elif test_period > getdate(self.last_working_days): 
			# 	frappe.msgprint(_("Employee is in test period"), alert=1)
			else:
				today = getdate(nowdate())
				notice_period_end_date = add_to_date(today, days=(notice_period_days-1))
				print(notice_period_end_date, "====", notice_period_days)
				if getdate(self.last_working_days) < getdate(notice_period_end_date):
					frappe.throw(_("Last Working Day must be after Notice Period"))

			if self.resignation_type == "Not Renew-Contract":
				resignation_date = self.last_working_days
				resignation_to_be_allow_date = add_to_date(getdate(resignation_date), days=notice_period_days)
				employee_contract_end_date = frappe.db.get_value("Employee", self.employee_no, 'contract_end_date')
				print(resignation_to_be_allow_date,"resignation_to_be_allow_date")
				if resignation_to_be_allow_date < getdate(employee_contract_end_date):
					print(resignation_to_be_allow_date, getdate(employee_contract_end_date))
					frappe.throw(_("You cannot resign before {0}".format(employee_contract_end_date)))
	
	def set_relieving_date_in_employee(self):
		emp =  frappe.get_doc("Employee", self.employee_no)
		emp.relieving_date = self.last_working_days
		emp.save(ignore_permissions=True)
		frappe.msgprint(_("In {0} Employee Relieving Date Set to {1}").format(self.employee_no, self.last_working_days), alert=1)

	@frappe.whitelist()
	def create_end_of_service(self):

		# Check Already Exist EOS
		eos_exists = frappe.db.exists("End of Service Calculation ST",{"resignation_reference": self.name})
		if eos_exists:
			frappe.throw(_("End of Service Calculation is Already Done."))

		# validate Allowed EOS Date
		allowed_eos_days = frappe.db.get_single_value('Stats Settings ST', 'eos_allowed_days_before_last_working_date')
		if cint(allowed_eos_days) > 0:
			valide_eos_date = add_to_date(getdate(self.last_working_days), days=-allowed_eos_days)
			# print(valide_eos_date, "========valide_eos_date============")

			if valide_eos_date > getdate(nowdate()):
				frappe.throw(_("You Cann't Create End Of Service Before {0} date.").format(valide_eos_date))


		eos = frappe.new_doc("End of Service Calculation ST")

		eos.resignation_reference = self.name
		eos.employee = self.employee_no
		eos.resignation_type = self.resignation_type
		eos.seperation_reason = self.separation_reason
		eos.end_of_service_type = "Resignation"

		eos.save(ignore_permissions=True)

		return eos.name
	
	@frappe.whitelist()
	def create_evacuation_of_party(self):
		# Check Already Exist Evacuation
		eop_exists = frappe.db.exists("Evacuation of Party ST",{"resignation_reference": self.name})
		if eop_exists:
			frappe.throw(_("Employee Evacuation is Already Done."))


		eop = frappe.new_doc("Evacuation of Party ST")

		eop.resignation_reference = self.name
		eop.employee_no = self.employee_no
		eop.last_working_days = self.last_working_days
		eop.insert(ignore_permissions=True, ignore_mandatory=True)

		return eop.name
	
	@frappe.whitelist()
	def create_exit_interview(self):
		# Check Already Exist Evacuation
		exit_interview_exists = frappe.db.exists("Exit Interview ST",{"resignation_reference": self.name})
		if exit_interview_exists:
			frappe.throw(_("Employee Exit Interview is Already Done."))

		ei = frappe.new_doc("Exit Interview ST")
		ei.resignation_reference = self.name
		ei.employee_no = self.employee_no

		ei.save(ignore_permissions=True)

		return ei.name
				
	@frappe.whitelist()
	def create_button_based_on_conditions(self):
		allow_to_create_eop = False
		allow_to_create_eos = False
		allow_to_create_ei = False

		eop_exists = frappe.db.exists("Evacuation of Party ST",{"resignation_reference":self.name})
		if eop_exists :
			eop_docstatus = frappe.db.get_value("Evacuation of Party ST",eop_exists,"docstatus")
			if eop_docstatus == 1 :
				allow_to_create_eop = False
				allow_to_create_eos = True
				allow_to_create_ei = False
			else :
				allow_to_create_eop, allow_to_create_eos, allow_to_create_ei = False, False, False
		else :
			allow_to_create_eop = True
			allow_to_create_eos = False
			allow_to_create_ei = False

		if allow_to_create_eop == False and allow_to_create_eos == True :
			eos_exists = frappe.db.exists("End of Service Calculation ST",{"resignation_reference":self.name})
			if eos_exists : 
				eos_docstatus = frappe.db.get_value("End of Service Calculation ST",eos_exists,"docstatus")
				if eos_docstatus == 1 :
					allow_to_create_eop = False
					allow_to_create_eos = False
					allow_to_create_ei = True
				else :
					allow_to_create_eop, allow_to_create_eos, allow_to_create_ei = False, False, False
			else :
				allow_to_create_eop = False
				allow_to_create_eos = True
				allow_to_create_ei = False

		if allow_to_create_eos == False and allow_to_create_eop == False and allow_to_create_ei == True :
			ei_exists = frappe.db.exists("Exit Interview ST",{"resignation_reference":self.name})
			if ei_exists : 
				ei_docstatus = frappe.db.get_value("Exit Interview ST",ei_exists,"docstatus")
				if ei_docstatus == 1 :
					allow_to_create_eop = False
					allow_to_create_eos = False
					allow_to_create_ei = False
				else :
					allow_to_create_eop, allow_to_create_eos, allow_to_create_ei = False, False, False
			else :
				allow_to_create_eop = False
				allow_to_create_eos = False
				allow_to_create_ei = True

		return {
			"allow_to_create_eop" : allow_to_create_eop,
			"allow_to_create_eos" : allow_to_create_eos,
			"allow_to_create_ei" : allow_to_create_ei
		}

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def check_employee_test_period(doctype, txt, searchfield, start, page_len, filters):
	employee = filters.get("employee")
	last_working_date = filters.get("last_working_days")

	emp_in_test_period = False

	emp_job_offer = frappe.db.get_value("Employee", employee, "custom_job_offer_reference")
	if emp_job_offer:
		emp_contract = frappe.get_all("Employee Contract ST", filters={"job_offer_reference": emp_job_offer}, fields=["name", "test_period_renewed", "test_period_end_date", "end_of_new_test_period"], limit=1)
		if len(emp_contract) > 0:
			contract = emp_contract[0]
			if contract.test_period_renewed == "No" and contract.test_period_end_date > getdate(last_working_date):
				emp_in_test_period = True
			elif contract.test_period_renewed == "Yes" and contract.end_of_new_test_period > getdate(last_working_date):
				emp_in_test_period = True

	if emp_in_test_period == True:
		resignation_type = frappe.get_all("Resignation Type ST", filters={"is_it_test_period_resignation":1, "name": ("like", f"{txt}%")}, fields=["distinct name"], as_list=1)
	else:
		resignation_type = frappe.get_all("Resignation Type ST", filters={"name": ("like", f"{txt}%")}, fields=["distinct name"], as_list=1)

	unique = tuple(set(resignation_type))

	return unique