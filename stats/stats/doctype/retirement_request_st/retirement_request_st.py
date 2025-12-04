# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from stats.salary import get_latest_salary_structure_assignment
# from hijridate import Hijri, Gregorian
from frappe.utils import cstr, getdate, cint, date_diff, nowdate
from hrms.hr.doctype.leave_application.leave_application import get_leave_details
from stats.hr_utils import set_date_in_hijri

class RetirementRequestST(Document):
	def validate(self):
		print('self.birth_date_hijri',self.birth_date_hijri)
		
		# self.retirement_date_gregorian=self.set_date_in_gregorian(self.retirement_date_hijri)
		self.validate_retirement_date()
		self.get_salary_details_and_due_amount_calculation()
		self.calculate_vacation_due_amount()
		self.calculate_total_due_amount()
		self.retirement_date_hijri = set_date_in_hijri(self.retirement_date_gregorian)

	# def set_date_in_gregorian(self,date_hijri) :
	# 	# https://hijri-converter.readthedocs.io/en/stable/usage.html
	# 	date_hijri=cstr(date_hijri)
	# 	hijri_splits=date_hijri.split('-')
	# 	g_date = Hijri(cint(hijri_splits[2]),cint(hijri_splits[1]),cint(hijri_splits[0])).to_gregorian()
	# 	g_date_formatte=getdate(g_date.dmyformat(separator='/'))
	# 	return getdate(g_date_formatte.strftime('%d-%m-%Y'))
	
	def validate_retirement_date(self):
		if getdate(self.birth_date_gregorian) >= getdate(self.retirement_date_gregorian):
			frappe.throw(_("Employee's Retirement Date Cannot be before Birth Date."))

	
	def get_salary_details_and_due_amount_calculation(self):
		basic_salary_component = frappe.db.get_value("Employee Grade", self.grade, "custom_basic_salary_component")
		salary_assignment = get_latest_salary_structure_assignment(self.employee_no, self.retirement_date_gregorian)
		if len(salary_assignment) > 0:
			self.salary_structure_assignment_reference = salary_assignment
			salary_structure = frappe.db.get_value("Salary Structure Assignment", salary_assignment, "salary_structure")
			ss = frappe.get_doc("Salary Structure", salary_structure)

			total_earnings = 0
			total_deductions = 0

			self.earning = []
			self.deduction = []

			retirement_due_amount = 0
			for ear in ss.earnings:
				eos_ear = self.append("earning", {})
				eos_ear.earning = ear.salary_component
				eos_ear.amount = ear.amount
				total_earnings = total_earnings + eos_ear.amount
				include_in_retirement_calculation = frappe.db.get_value("Salary Component", ear.salary_component, "custom_include_in_retirement_calculation")
				if include_in_retirement_calculation == 1:
					retirement_due_amount = retirement_due_amount + ear.amount

				if basic_salary_component and basic_salary_component == eos_ear.earning:
					self.basic_salary = eos_ear.amount

			for ded in ss.deductions:
				eos_ded = self.append("deduction", {})
				eos_ded.deduction = ded.salary_component
				eos_ded.amount = ded.amount
				total_deductions = total_deductions + eos_ded.amount
	
			self.total_monthly_salary = total_earnings
			self.total_monthly_deduction = total_deductions
			self.net_salary = self.total_monthly_salary - self.total_monthly_deduction
			# self.retirement_due_amount = retirement_due_amount
			# self.new_retirement_due_amount = (self.retirement_due_amount - (self.social_dev_bank_deduction or 0)
			# 							 - (self.agricalture_dev_bank_deduction or 0)- (self.real_stat_dev_bank_deduction or 0))
			
			######### retirement due amount #########

			age_diff_in_days = date_diff(self.retirement_date_gregorian, self.birth_date_gregorian)
			# age_diff_in_years = age_diff_in_days / 360
			self.age_duration_days = age_diff_in_days
			age_diff_in_years_hijri = age_diff_in_days / 354
			self.age_duration_years = age_diff_in_years_hijri
			# self.age_duration_years = age_diff_in_years

			normal_years_of_retirement = frappe.db.get_value("Contract Type ST", self.contract_type, "normal_years_of_retirement")
			if normal_years_of_retirement and self.age_duration_years >= normal_years_of_retirement:
				self.retirement_type = "Normal Retirement"
				self.retirement_due_amount = retirement_due_amount * 6
			else:
				self.retirement_type = "Early Retirement"
				self.retirement_due_amount = retirement_due_amount * 4

			######## work duration calculation ########
			work_duration_in_days = date_diff(self.retirement_date_gregorian, self.employee_joining_date)
			self.work_duration_days = work_duration_in_days
										

	def calculate_vacation_due_amount(self):
		########## vacation days calculation #########

		contract_type = frappe.db.get_value("Employee", self.employee_no, "custom_contract_type")
		considered_vacation_days = frappe.db.get_value("Contract Type ST", contract_type, "considered_vacation_days")
		salary_assignment = get_latest_salary_structure_assignment(self.employee_no, self.retirement_date_gregorian)
		total_monthly_salary = frappe.db.get_value("Salary Structure Assignment", salary_assignment, "base")
		per_day_salary_for_vacation = (self.basic_salary or 0) / 30
		
		if considered_vacation_days:
			self.considered_vacation_days = considered_vacation_days

			leave_types = frappe.db.sql_list("select name from `tabLeave Type` where custom_allow_encasement_end_of_service = 1 order by name asc")

			# available_leave = get_leave_details(self.employee, "2024-11-26")
			available_leave = get_leave_details(self.employee_no, getdate(nowdate()))
			if len(available_leave["leave_allocation"]) > 0:
				total_considered_vacation_days = 0
				for leave_type in leave_types:
					remaining = 0
					if leave_type in available_leave["leave_allocation"]:
						remaining = available_leave["leave_allocation"][leave_type]["remaining_leaves"]
					total_considered_vacation_days = total_considered_vacation_days + remaining

					print(leave_type, "===leave_type",remaining, "====remaining")
					print(total_considered_vacation_days, "==total_considered_vacation_days")

				self.due_vacation_balance = total_considered_vacation_days

				if self.considered_vacation_days < self.due_vacation_balance:
					self.vacation_due_amount = per_day_salary_for_vacation * self.considered_vacation_days
				else:
					self.vacation_due_amount = per_day_salary_for_vacation * self.due_vacation_balance

			else:
				frappe.throw(_("Leave Allocation is not found for {0} employee for {1} date.").format(self.employee_no, getdate(nowdate())))

	def calculate_total_due_amount(self):
		self.new_retirement_due_amount = (self.retirement_due_amount - (self.social_dev_bank_deduction or 0)
										 - (self.agricalture_dev_bank_deduction or 0)- (self.real_stat_dev_bank_deduction or 0))
		
		self.total_due_amount = (self.new_retirement_due_amount or 0) +( self.vacation_due_amount or 0)

	@frappe.whitelist()
	def create_evacuation_of_party(self):
		eop = frappe.new_doc("Evacuation of Party ST")

		eop.retirement_reference = self.name
		eop.employee_no = self.employee_no
		eop.last_working_days = self.retirement_date_gregorian
		eop.insert(ignore_permissions=True, ignore_mandatory=True)

		return eop.name
	
	@frappe.whitelist()
	def create_exit_interview(self):
		ei = frappe.new_doc("Exit Interview ST")
		ei.retirement_reference = self.name
		ei.employee_no = self.employee_no

		ei.save(ignore_permissions=True)

		return ei.name
 
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_civil_employee(doctype, txt, searchfield, start, page_len, filters):
	employee = frappe.db.get_all("Employee", filters={"status":"Active"}, fields=["name", "custom_contract_type", "employee_name"])

	civil_employees = []
	for emp in employee:
		contract_type = frappe.db.get_value("Contract Type ST", emp.custom_contract_type, "contract")
		if contract_type == "Civil":
			employee_name = (emp.get('name'),emp.get('employee_name'),)
			civil_employees.append(employee_name)
		else:
			continue

	return civil_employees
