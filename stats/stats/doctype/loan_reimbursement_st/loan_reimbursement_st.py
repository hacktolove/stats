# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date, getdate, today, cint
from erpnext.accounts.utils import get_fiscal_year

class LoanReimbursementST(Document):
	def validate(self):
		self.calculate_instalments()
		self.add_rows_in_table_of_discounts()

	def before_submit(self):
		# self.add_rows_in_table_of_discounts()
		self.create_additional_salary_for_each_instalment()

	def on_update_after_submit(self):
		self.on_early_payment_cancel_additional_salary()
	
	def calculate_instalments(self):
		self.first_instalment = self.instalment_value

		last_instalment = self.total_amount % self.instalment_value

		if last_instalment == 0:
			self.last_instalment = self.instalment_value
			self.number_of_instalments = self.total_amount // self.instalment_value
		else:
			self.last_instalment = last_instalment
			self.number_of_instalments = (self.total_amount // self.instalment_value) + 1


	def add_rows_in_table_of_discounts(self):
		if self.number_of_instalments and self.number_of_instalments > 0:
			self.table_of_discounts = []

			deduction_date = self.deduction_start_date
			for x in range(cint(self.number_of_instalments)):
				if (x + 1) == self.number_of_instalments:
					row = self.append('table_of_discounts', {})
					row.instalment_value = self.last_instalment
				else:
					row = self.append('table_of_discounts', {})	
					row.instalment_value = self.first_instalment

				if self.is_past_data == 1:
					row.status = "Deducted"
				else:
					row.status = "Scheduled"
				row.deduction_date = deduction_date
				row.fiscal_year = get_fiscal_year(row.deduction_date)[0]
				row.month = getdate(row.deduction_date).strftime("%b")
				# months = getdate(row.deduction_date).strftime("%B")
				# row.month = getdate(row.deduction_date).month
				deduction_date =add_to_date(deduction_date, months=1)
			
			self.deduction_end_date = add_to_date(deduction_date, months=-1)

	def create_additional_salary_for_each_instalment(self):
		if self.is_past_data == 0:
			for row in self.table_of_discounts:
				add_salary = frappe.new_doc("Additional Salary")
				add_salary.employee = self.employee_no
				add_salary.salary_component = self.salary_component
				add_salary.amount = row.instalment_value
				add_salary.payroll_date = row.deduction_date
				add_salary.submit()
				row.additional_salary_ref = add_salary.name
				frappe.msgprint(_("Additional Salary {0} created").format(row.additional_salary_ref), alert=True)

	def on_early_payment_cancel_additional_salary(self):
		if self.status == "Early Payment" and self.docstatus == 1:
			if len(self.table_of_discounts) > 0:
				for row in self.table_of_discounts:
					additional_salary = frappe.get_doc("Additional Salary", row.additional_salary_ref)
					if additional_salary:
						if additional_salary.docstatus == 1 and additional_salary.payroll_date > getdate(today()):
							additional_salary.cancel()
							frappe.msgprint(_("Additional Salary {0} cancelled").format(additional_salary.name), alert=True)