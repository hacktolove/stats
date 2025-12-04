# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document
import erpnext
from stats.api import create_journal_entry_for_petty_cash

class PettyCashClosingST(Document):
	
	def validate(self):
		self.calculate_paid_unpaid_amount()
		self.set_paid_amount_from_expense_accounts_table()

	def on_submit(self):
		self.validate_expense_account_details_and_pc_closing_account_details()
		self.validate_paid_amount()
		self.create_journal_entry()
		self.change_status_of_pc_request()

	def calculate_paid_unpaid_amount(self):
		total_requested_amount = self.total_requested_amount
		total_paid_amount = 0
		if len(self.expense_account_details)>0:
			for row in self.expense_account_details:
				# total_requested_amount = total_requested_amount + row.amount
				if row.amount:
					total_paid_amount = total_paid_amount + row.amount
			self.total_paid_amount = total_paid_amount
			self.total_unpaid_amount = total_requested_amount - total_paid_amount
		else:
			self.total_paid_amount = 0
			self.total_unpaid_amount = 0
		print(total_requested_amount,total_paid_amount,"===========================")
		if total_paid_amount > total_requested_amount:
			frappe.throw(_("Total Expense Amount cannot be greater than Total Requested Amount"))
		
	def set_paid_amount_from_expense_accounts_table(self):
		if len(self.pc_closing_account_details)>0:
			for row in self.pc_closing_account_details:
				row.paid_amount = self.total_paid_amount
				row.unpaid_amount = self.total_unpaid_amount
	
	def validate_expense_account_details_and_pc_closing_account_details(self):
		if len(self.expense_account_details)==0:
			frappe.throw(_("Please add Expense Account Details"))
		if len(self.pc_closing_account_details)==0:
			frappe.throw(_("Please add PC Closing Account Details"))

	def validate_paid_amount(self):
		if len(self.pc_closing_account_details)>0:
			for row in self.pc_closing_account_details:
				if not row.paid_amount:
					frappe.throw(_("#Row {0}: Please fill paid amount in PC Closing Account Details".format(row.idx)))

	def change_status_of_pc_request(self):
		if self.petty_cash_request_reference:
			pc_request_doc = frappe.get_doc("Petty Cash Request ST",self.petty_cash_request_reference)
			pc_request_doc.loan_status = "Closed"
			pc_request_doc.add_comment("Comment",text = "Loan Status changed to Closed due to {0}".format(get_link_to_form("Petty Cash Closing ST",self.name)))
			pc_request_doc.save(ignore_permissions=True)
			frappe.msgprint(_("PC Request {0} Loan status changed to <b>Closed</b>".format(get_link_to_form("Petty Cash Request ST",self.petty_cash_request_reference))),alert=True)
	
	def create_journal_entry(self):

		department_cost_center = frappe.db.get_value("Department",self.main_department,"custom_department_cost_center")
		company = erpnext.get_default_company()
		company_default_employee_petty_cash_account = frappe.db.get_value("Company",company,"custom_default_employee_petty_cash_account")
		company_default_pending_income_account = frappe.db.get_value("Company",company,"custom_default_pending_income_account")
		company_default_revenue_account = frappe.db.get_value("Company",company,"custom_default_revenue_account")
		company_default_bank_account = frappe.db.get_value("Company",company,"default_bank_account")
		company_default_debit_account_mof = frappe.db.get_value("Company",company,"custom_default_debit_account_mof")
		total_amount = 0

		jv_doc = frappe.new_doc("Journal Entry")
		jv_doc.voucher_type = "Journal Entry"
		jv_doc.posting_date = self.creation_date
		jv_doc.custom_petty_cash_closing_reference = self.name
		jv_doc.remark = "Journal Entry for Petty Cash Closing ST: {0}".format(self.name)

		if len(self.expense_account_details)>0:
			for row in self.expense_account_details:
				jv_row = jv_doc.append("accounts", {})
				jv_row.account = row.account_name
				jv_row.debit_in_account_currency = row.amount
				account_type = frappe.get_cached_value("Account",row.account_name, "account_type")
				if account_type in ["Receivable", "Payable"]:
					jv_row.party_type="Employee"
					jv_row.party=self.employee_no

				jv_row.cost_center = department_cost_center

				total_amount = total_amount + row.amount

	
		jv_row = jv_doc.append("accounts", {})
		jv_row.account = company_default_employee_petty_cash_account
		jv_row.credit_in_account_currency = total_amount
		account_type = frappe.get_cached_value("Account",company_default_employee_petty_cash_account, "account_type")
		if account_type in ["Receivable", "Payable"]:
			jv_row.party_type="Employee"
			jv_row.party=self.employee_no

		jv_row.cost_center = department_cost_center

		jv_doc.run_method('set_missing_values')
		jv_doc.save(ignore_permissions = True)
		jv_doc.submit()
		self.journal_entry_reference = jv_doc.name
		frappe.msgprint(_("Journal Entry {0} created successfully").format(get_link_to_form("Journal Entry",jv_doc.name)),alert=True)
	
		create_journal_entry_for_petty_cash(self,company_default_pending_income_account,company_default_revenue_account,total_amount,self.main_department,je_date=None,party_type="Employee",party_name=self.employee_no,jv_type="Closing")

		# if there is unpaid amount then create JE to record liability
		if self.total_unpaid_amount > 0:
			create_journal_entry_for_petty_cash(self,company_default_bank_account,company_default_employee_petty_cash_account,self.total_unpaid_amount,self.main_department,je_date=None,party_type="Employee",party_name=self.employee_no,jv_type="Closing")
			create_journal_entry_for_petty_cash(self,company_default_pending_income_account,company_default_debit_account_mof,self.total_unpaid_amount,self.main_department,je_date=None,party_type="Employee",party_name=self.employee_no,jv_type="Closing")

	@frappe.whitelist()
	def create_petty_cash_repayment(self):
		pc_repayment_doc = frappe.new_doc("Petty Cash Re-Payment ST")
		pc_repayment_doc.petty_cash_closing_reference = self.name
		pc_repayment_doc.petty_cash_request_reference = self.petty_cash_request_reference
		pc_repayment_doc.deposit_amount = self.total_unpaid_amount
		pc_repayment_doc.total_unpaid = self.total_unpaid_amount

		if len(self.pc_closing_account_details)>0:
			for row in self.pc_closing_account_details:
				pc_repayment_row = pc_repayment_doc.append("pc_repayment_account_details", {})
				pc_repayment_row.account_name = row.account_name
				pc_repayment_row.amount = row.amount
				pc_repayment_row.paid_amount = row.paid_amount
				pc_repayment_row.unpaid_amount = row.unpaid_amount
			
		pc_repayment_doc.run_method('set_missing_values')
		pc_repayment_doc.save(ignore_permissions = True)
		print(pc_repayment_doc.name,"--------------------------------------")
		return pc_repayment_doc.name