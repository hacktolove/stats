# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date, date_diff, get_link_to_form, getdate, nowdate, get_last_day, get_first_day, month_diff, cint, flt
from stats.salary import get_latest_salary_structure_assignment
from hrms.hr.doctype.leave_application.leave_application import get_leave_details

class EndofServiceCalculationST(Document):
	def validate(self):
		self.check_already_exists_eos()
		self.get_salary_details()
		self.calculate_end_of_service_due_amount()
		self.calculate_vacation_due_amount()

	def on_submit(self):
		resignation_doc = frappe.get_doc("Employee Resignation ST", self.resignation_reference)
		resignation_doc.end_of_service_calculation_status = "Processed"
		frappe.msgprint(_("In Employee Resignation: {0} End OF Service Calculation Status Set to 'Processed'.").format(self.resignation_reference), alert=1)
		resignation_doc.add_comment("Comment",text="End OF Service Calculation Status Set to <b>Processed</b> due to {0}".format(get_link_to_form(self.doctype,self.name)))
		resignation_doc.save(ignore_permissions=True)

	def on_trash(self):
		if self.resignation_reference:
			resignation_doc = frappe.get_doc("Employee Resignation ST", self.resignation_reference)
			resignation_doc.end_of_service_calculation_status = "Pending"
			frappe.msgprint(_("In Employee Resignation: {0} End OF Service Calculation Status Set to 'Pending'.").format(self.resignation_reference), alert=1)
			resignation_doc.add_comment("Comment",text="End OF Service Calculation Status Set to <b>Pending</b> due to delete {0} document".format(self.name))
			resignation_doc.save(ignore_permissions=True)

	def check_already_exists_eos(self):
		eos_exists = frappe.db.exists("End of Service Calculation ST",{"resignation_reference": self.resignation_reference, "name": ["!=", self.name]})
		if eos_exists:
			frappe.throw(_("End of Service Calculation for {0} Resignation Request is Already Done.").format(self.resignation_reference))

		if self.resignation_reference:
			resignation_status = frappe.db.get_value("Employee Resignation ST", self.resignation_reference, "docstatus")
			if resignation_status != 1:
				frappe.throw(_("End of Service Calculation can be created only for Submitted Employee Resignation."))

	def get_salary_details(self):
		salary_assignment = get_latest_salary_structure_assignment(self.employee, self.last_working_date)
		if len(salary_assignment) > 0:
			self.salary_structure_assignment_reference = salary_assignment
			salary_structure = frappe.db.get_value("Salary Structure Assignment", salary_assignment, "salary_structure")
			ss = frappe.get_doc("Salary Structure", salary_structure)

			total_earnings = 0
			total_deductions = 0

			self.earning = []
			self.deduction = []
			for ear in ss.earnings:
				eos_ear = self.append("earning", {})
				eos_ear.earning = ear.salary_component
				eos_ear.amount = ear.amount
				total_earnings = total_earnings + eos_ear.amount

			for ded in ss.deductions:
				eos_ded = self.append("deduction", {})
				eos_ded.deduction = ded.salary_component
				eos_ded.amount = ded.amount
				total_deductions = total_deductions + eos_ded.amount

			
			self.total_monthly_salary = total_earnings
			self.total_monthly_deduction = total_deductions
			self.net_salary = self.total_monthly_salary - self.total_monthly_deduction

	def calculate_end_of_service_due_amount(self):

		########## working days calculation #########

		joining_date = self.joining_date
		last_working_date = self.last_working_date
		# total_no_of_working_days = date_diff(last_working_date, joining_date)

		print(no_of_days_in_start_date_month(joining_date), '-----no_of_days_in_start_date_month(joining_date)')
		print(no_months_days_between_dates(joining_date, last_working_date) * 30, "----no_months_days_between_dates(joining_date, last_working_date) * 30")
		print(no_of_days_in_end_date(last_working_date), '----no_of_days_in_end_date(last_working_date)')

		total_no_of_working_days = no_of_days_in_start_date_month(joining_date) + ( no_months_days_between_dates(joining_date, last_working_date) * 30) + no_of_days_in_end_date(last_working_date)

		no_of_days_in_last_year_of_service = total_no_of_working_days % 360
		no_of_full_years_in_service = total_no_of_working_days - no_of_days_in_last_year_of_service
		years = no_of_full_years_in_service / 360

		self.total_no_of_working_days = total_no_of_working_days
		self.no_of_full_years_in_service = years
		self.no_of_days_in_last_year_of_service = no_of_days_in_last_year_of_service

		####### due amount calculation ########

		full_salary = self.total_monthly_salary
		half_salary = full_salary / 2
		years = no_of_full_years_in_service / 360

		per_year_due_amount = 0
		per_day_due_amount = 0
		eos_due_amount = 0

		regination_type = frappe.get_doc("Resignation Type ST", self.resignation_type)

		if regination_type.is_it_resignation == 1:
			if self.total_no_of_working_days > 720 and self.total_no_of_working_days < 1800:
				per_year_due_amount = (half_salary / 3)
				total_years_due_amount =per_year_due_amount * years
				per_day_due_amount = per_year_due_amount/360
				last_year_days_due_amount = per_day_due_amount * self.no_of_days_in_last_year_of_service

				eos_due_amount = total_years_due_amount + last_year_days_due_amount

			elif self.total_no_of_working_days > 1800:
				per_year_due_amount = full_salary
				total_years_due_amount = per_year_due_amount * years
				per_day_due_amount = per_year_due_amount /360
				last_year_days_due_amount = per_day_due_amount * self.no_of_days_in_last_year_of_service

				eos_due_amount = total_years_due_amount + last_year_days_due_amount

			else:
				eos_due_amount = 0

		elif regination_type.is_it_not_renewal_of_contract == 1:
			if self.total_no_of_working_days > 1800:
				per_year_due_amount = half_salary
				total_years_due_amount = per_year_due_amount * years
				per_day_due_amount = per_year_due_amount /360
				last_year_days_due_amount = per_day_due_amount * self.no_of_days_in_last_year_of_service

				eos_due_amount = total_years_due_amount + last_year_days_due_amount
			else:
				per_year_due_amount = full_salary
				total_years_due_amount = per_year_due_amount * years
				per_day_due_amount = per_year_due_amount /360
				last_year_days_due_amount = per_day_due_amount * self.no_of_days_in_last_year_of_service

				eos_due_amount = total_years_due_amount + last_year_days_due_amount

		self.per_day_eos_due_amount = per_day_due_amount
		self.per_year_eos_due_amount = per_year_due_amount
		self.end_of_service_due_amount = eos_due_amount

	def calculate_vacation_due_amount(self):
		########## vacation days calculation #########

		contract_type = frappe.db.get_value("Employee", self.employee, "custom_contract_type")
		considered_vacation_days, monthly_leave_balance = frappe.db.get_value("Contract Type ST", contract_type, ["considered_vacation_days", "monthly_leave_balance"])

		total_monthly_salary = self.total_monthly_salary
		# per_day_salary = total_monthly_salary / 360
		per_day_salary_for_vacation = total_monthly_salary / 30
		
		if considered_vacation_days:
			self.considered_vacation_days = considered_vacation_days

		leave_types = frappe.db.sql_list("select name from `tabLeave Type` where custom_allow_encasement_end_of_service = 1 order by name asc")

		# available_leave = get_leave_details(self.employee, "2024-11-26")
		available_leave = get_leave_details(self.employee, getdate(nowdate()))
		if len(available_leave["leave_allocation"]) > 0:
			total_considered_vacation_days = 0
			for leave_type in leave_types:
				remaining = 0
				if leave_type in available_leave["leave_allocation"]:
					remaining = available_leave["leave_allocation"][leave_type]["remaining_leaves"]
				total_considered_vacation_days = total_considered_vacation_days + remaining

				# print(leave_type, "===leave_type",remaining, "====remaining") 
				print(total_considered_vacation_days, "==total_considered_vacation_days")
			
			if monthly_leave_balance:
				# print(monthly_leave_balance, "=============monthly_leave_balance=================")
				last_month_leave_balance = flt(((monthly_leave_balance/ 30) * (getdate(self.last_working_date).day)), 2)
				# print(last_month_leave_balance, "=======================last_month_leave_balance===============")
				total_considered_vacation_days = total_considered_vacation_days + last_month_leave_balance

			self.vacation_balance = flt((total_considered_vacation_days), 2)

			if self.considered_vacation_days < self.vacation_balance:
				self.vacation_due_amount = per_day_salary_for_vacation * cint(self.considered_vacation_days)
			else:
				self.vacation_due_amount = per_day_salary_for_vacation * self.vacation_balance

		else:
			frappe.throw(_("Leave Allocation is not found for {0} employee for {1} date.").format(self.employee, getdate(nowdate())))

def no_of_days_in_start_date_month(start_date):
	month_end_date = get_last_day(getdate(start_date))
	no_of_days = date_diff(getdate(month_end_date), getdate(start_date)) + 1
	print(no_of_days, '----no_of_days')
	return no_of_days

def no_months_days_between_dates(start_date, end_date):
	start_date_month_end_date = get_last_day(getdate(start_date))
	next_month_start_date = add_to_date(getdate(start_date_month_end_date), days=1)
	print(next_month_start_date, '-----next_month_start_date---')

	first_date_of_end_date_month = get_first_day(getdate(end_date))
	previous_month_end_date = add_to_date(getdate(first_date_of_end_date_month), days=-1)
	print(previous_month_end_date, '----previous_month_end_date---')

	total_months = (month_diff(getdate(previous_month_end_date), getdate(next_month_start_date)))
	print(total_months, '-----total_months')

	return total_months

def no_of_days_in_end_date(end_date):
	days = getdate(end_date).day
	print(days, '-----days--')
	return days