# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document
from frappe.utils import add_to_date,add_years,getdate
from stats.api import get_monthly_salary_from_job_offer
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee

class EmployeeContractST(Document):
	def validate(self):
		self.validate_trial_period()
		self.set_total_monthly_salary()

	def on_submit(self):
		self.create_salary_structure()
		self.set_contract_dates_in_employee()

	@frappe.whitelist()
	def validate_trial_period(self):
		if self.contract_start_date:
			test_period_end_date = add_to_date(self.contract_start_date, months=3)
			contract_end_date = add_years(self.contract_start_date, 1)
			self.contract_end_date = add_to_date(getdate(contract_end_date), days=-1)
			end_of_new_test_period = add_to_date(self.test_period_end_date, months=3)

			####### Add General Holidays #######
			self.test_period_end_date = self.add_general_holidays_in_end_date(test_period_end_date)
			if self.test_period_renewed == "Yes":
				self.end_of_new_test_period = self.add_general_holidays_in_end_date(end_of_new_test_period)
			else:
				self.end_of_new_test_period = None
	
	def add_general_holidays_in_end_date(self, end_date):
		holiday_list = get_holiday_list_for_employee(self.employee_no, raise_exception=True)
		general_holidays = frappe.db.get_all("Holiday", filters = {'parent': holiday_list, 'weekly_off' : 0}, pluck ='holiday_date')

		if len(general_holidays) > 0:
			for holiday in general_holidays:
				if getdate(holiday) >= getdate(self.contract_start_date) and getdate(holiday) <= getdate(end_date):
					end_date = add_to_date(getdate(end_date), days=1)
					while(getdate(end_date) in general_holidays):
						end_date = add_to_date(getdate(end_date), days=1)
		
		return end_date

	def set_total_monthly_salary(self):
		total_monthly_salary = 0
		if len(self.earnings_details) > 0:
			for ear in self.earnings_details:
				total_monthly_salary = total_monthly_salary + ear.amount

		self.total_monthly_salary = total_monthly_salary

	def on_update_after_submit(self):
		if self.test_period_renewed == "Yes":
			self.end_of_new_test_period = add_to_date(self.test_period_end_date, months=3)

	def create_salary_structure(self):
		if self.contract_type:
			salary_structure = frappe.new_doc("Salary Structure")
			salary_structure.__newname = self.employee_no + "/" + self.name
			salary_structure.name = self.employee_no + "/" + self.name
			salary_structure.custom_employee_contract_ref = self.name
			salary_structure.custom_employee_no = self.employee_no
			salary_structure.custom_contract_start_date = self.contract_start_date

			if len(self.earnings_details) > 0:
				for ear in self.earnings_details:
					earning = salary_structure.append("earnings", {})
					earning.salary_component = ear.earning
					earning.amount = ear.amount
					earning.amount_based_on_formula = 0
					earning.is_tax_applicable = 0
					earning.depends_on_payment_days = 0
			
			if len(self.deduction_details) > 0:
				for ded in self.deduction_details:
					deduction = salary_structure.append("deductions", {})
					deduction.salary_component = ded.deduction
					deduction.amount = ded.amount
					deduction.amount_based_on_formula = 0
					deduction.is_tax_applicable = 0
					deduction.depends_on_payment_days = 0
			
			salary_structure.save(ignore_permissions=True)

			frappe.msgprint(_("Salary Structure {0} is created."
					 .format(get_link_to_form('Salary Structure', salary_structure.name))), alert=True)
			
			salary_structure.submit()
	
	def set_contract_dates_in_employee(self):
		frappe.db.set_value("Employee", self.employee_no, "custom_contract_start_date", self.contract_start_date)
		frappe.db.set_value("Employee", self.employee_no, "contract_end_date", self.contract_end_date)

@frappe.whitelist()
def get_salary_details(parent, parenttype):

	earning = frappe.get_all(
		"Grade Earnings Amount Details ST",
		fields=[
			"earning",
			"abbr",
			"percentage",
			"amount",
			"maximum_amount",
			"minimum_amount",
			"method"
		],
		filters={"parent": parent, "parenttype": parenttype},
		order_by="idx",
	)

	deduction = frappe.get_all(
		"Grade Deductions Amount Details ST",
		fields=[
			"deduction",
			"abbr",
			"formula",
			"amount"
		],
		filters={"parent": parent, "parenttype": parenttype},
		order_by="idx",
	)

	return earning, deduction