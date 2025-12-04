# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, get_link_to_form, flt, get_first_day, add_to_date, getdate, cint
from stats.api import get_base_amount_from_salary_structure_assignment

class EmployeePenaltyST(Document):
	def validate(self):
		self.fetch_penalty_details_from_violation_type()

	def on_submit(self):
		self.add_penalty_in_employee()
		self.create_additional_salary()
		self.create_resignation_for_seperation()


	def fetch_penalty_details_from_violation_type(self):
		prev_emp_penalty = frappe.db.count('Employee Penalty ST', {'employee': self.employee, 
															'violation_type':self.violation_type, 'name':['!=', self.name], 'docstatus':1})
		print(prev_emp_penalty, '---count-----------')
		base = get_base_amount_from_salary_structure_assignment(self.employee)
		if base == 0:
			frappe.throw(_("In Salary Structure Assignment, Base Amount cannot be zero for {0} Employee").format(self.employee))
		else:
			if prev_emp_penalty == 0:
				violation = frappe.get_doc("Violation ST", self.violation_type)
				for pen in violation.penalty:
					if pen.recurrence_type == "First Time":
						self.action_type = pen.action_type
						self.deduction = pen.deduction
						# self.deduction = flt(((base/30)*(pen.deduction/100)),2)
						break
					# else:
					# 	frappe.throw(_("In Violation type: {0} First Time Penalty is not define.").format( self.violation_type))
			
			if prev_emp_penalty == 1:
				violation = frappe.get_doc("Violation ST", self.violation_type)
				for pen in violation.penalty:
					if pen.recurrence_type == "Second Time":
						self.action_type = pen.action_type
						self.deduction = pen.deduction
						# self.deduction = flt((((base/30)*(pen.deduction/100)) / 100),2)
						break
					# else:
					# 	frappe.throw(_("In Violation type: {0} Second Time Penalty is not define.").format( self.violation_type))

			if prev_emp_penalty == 2:
				violation = frappe.get_doc("Violation ST", self.violation_type)
				for pen in violation.penalty:
					if pen.recurrence_type == "Third Time":
						self.action_type = pen.action_type
						self.deduction = pen.deduction
						# self.deduction = flt((((base/30)*(pen.deduction/100)) / 100),2)
						break
					# else:
					# 	frappe.throw(_("In Violation type: {0} Third Time Penalty is not define.").format( self.violation_type))

			if prev_emp_penalty >= 3:
				print(prev_emp_penalty, '---prev_emp_penalty')
				violation = frappe.get_doc("Violation ST", self.violation_type)
				for pen in violation.penalty:
					print(pen.recurrence_type, '---pen.recurrence_type')
					if pen.recurrence_type == "Fourth Time":
						self.action_type = pen.action_type
						self.deduction = pen.deduction
						# self.deduction = flt((((base/30)*(pen.deduction/100)) / 100),2)
						break
					# else:
					# 	frappe.throw(_("In Violation type: {0} Fourth Time Penalty is not define.").format( self.violation_type))

			self.recurrence_count_of_violation = prev_emp_penalty + 1

	def add_penalty_in_employee(self):
		print("in side submit")
		employee = frappe.get_doc("Employee", self.employee)
		row =  employee.append("custom_penalty_history_details", {})
		row.penalty_reference = self.name
		row.penalty_date = nowdate()
		row.type_of_penalty = self.violation_type
		row.recurrence_type = self.recurrence_count_of_violation
		row.action_type = self.action_type
		print(row.penalty_reference, '---penalty_reference')
		employee.save(ignore_permissions = True)
		frappe.msgprint(_("Penalty added in Employee {0}'s Penalty History Table.").format(employee.name), alert=1)

	def create_additional_salary(self):
		if self.deduction > 0 and self.action_type != "Separation":
			base = get_base_amount_from_salary_structure_assignment(self.employee)
			penalty_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'penalty_deduction_component')
			
			today_month = getdate(nowdate()).month
			today_year = getdate(nowdate()).year
			penalty_month = getdate(self.penalty_date).month
			penalty_year = getdate(self.penalty_date).year

			additional_salary = frappe.new_doc("Additional Salary")
			additional_salary.employee = self.employee
			# additional_salary.payroll_date = get_first_day(next_month_date)
			additional_salary.salary_component = penalty_deduction_component
			per_day_salary = (base/30)
			additional_salary.amount = per_day_salary * (self.deduction / 100)
			# print(self.deduction, '----self.deduction', base, '======base')
			# print(additional_salary.amount, '========== additional_salary.amount ===============')
			additional_salary.overwrite_salary_structure_amount = 0

			if (today_month == penalty_month) and (today_year == penalty_year):	
				payroll_date = frappe.db.get_single_value('Stats Settings ST', 'every_month_payroll_date')
				if payroll_date == None:
					frappe.throw(_("Please Set Every Month Payroll Date In Stats Settings."))

				penalty_day = getdate(self.penalty_date).day
				if penalty_day >= cint(payroll_date):
					next_month_date = add_to_date(self.penalty_date, months=1)
					print("start after payroll")
					additional_salary.payroll_date = get_first_day(next_month_date)
				else:
					print("start before payroll")
					additional_salary.payroll_date = getdate(self.penalty_date)

			else:
				additional_salary.payroll_date = getdate(self.penalty_date)

			print(additional_salary.payroll_date, '===additional_salary.payroll_date')

			additional_salary.save(ignore_permissions = True)
			frappe.msgprint(_("Additional Salary {0} created." .format(get_link_to_form('Additional Salary', additional_salary.name))), alert=True)
			additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for Penalty Deduction'.format(nowdate()))
			additional_salary.submit()

	def create_resignation_for_seperation(self):
		if self.action_type == "Separation":
			separation_resignation_type = frappe.db.get_single_value('Stats Settings ST', 'penalty_separation_resignation_type')
			if not separation_resignation_type:
				frappe.throw(_("Please Set Penalty Separation Resignation Type in Stats Settings."))

			res = frappe.new_doc("Employee Resignation ST")
			res.employee_penalty_ref = self.name
			res.resignation_date = nowdate()
			res.employee_no = self.employee
			res.last_working_days = nowdate()
			res.description_of_the_violation = self.description_of_the_violation
			res.legal_committee_recommendation = self.legal_committee_recommendation
			res.resignation_type = separation_resignation_type

			res.save(ignore_permissions = True)

			frappe.msgprint(_("Employee Resignation {0} created." .format(get_link_to_form('Employee Resignation ST', res.name))), alert=True)