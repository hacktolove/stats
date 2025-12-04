# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from stats.constants import BUDGET_EXPENSE_ACCOUNT
from frappe import _
from frappe.utils import get_link_to_form
from stats.api import create_budget
from frappe.utils import flt
# from stats.stats.doctype.department_budget_st.department_budget_st import create_budget

class DepartmentBudgetST(Document):
	def validate(self):
		self.calculate_total_requested_amount()
		self.calculate_net_balance()
		self.validate_duplicate_account()
		self.validate_duplicate_department_budget_entry()

	def on_cancel(self):
		for row in self.account_table:
			if frappe.db.exists("Department Wise Budget Allocation Details ST", {"department_acct_details_name": row.name, "docstatus":1}):
				frappe.throw(_("You cannot delete this department budget because of Accumulative Budget is created."))
		self.cancel_connected_budget()

	def on_update_after_submit(self):

		self.calculate_net_balance()
		self.initial_budget_updates()
		# self.create_budget()
		# print('on_update_after_submit===', self.name)

	def calculate_total_requested_amount(self):
		total_amount = 0
		if len(self.account_table)>0:
			for row in self.account_table:
				total_amount = total_amount + row.requested_amount

		self.total_requested_amount = total_amount


	def calculate_net_balance(self):
		if len(self.account_table)>0:
			for row in self.account_table:
				net_balance = flt(((row.approved_amount or 0) + (row.previous_balance or 0)),2)
				row.net_balance = net_balance
				frappe.db.set_value(row.doctype, row.name, 'net_balance', net_balance)

	def validate_duplicate_account(self):
		if len(self.account_table) > 1:
			account_name=[]
			for acc in self.account_table:
				if acc.budget_expense_account in account_name:
						frappe.throw(_("You cannot use same account multiple time"))
				else:
					account_name.append(acc.budget_expense_account)
	
	def validate_duplicate_department_budget_entry(self):
		if self.is_new():
			if frappe.db.exists("Department Budget ST", {"fiscal_year": self.fiscal_year, "main_department":self.main_department,"docstatus":["!=",2]}):
				frappe.throw(_("In {0} fiscal year for {1} Department Budget is already created").format(self.fiscal_year, self.main_department))
				pass

	def initial_budget_updates(self):
		if len(self.account_table) > 0:
			for acc in self.account_table:
				for bud in self.budget_update:
					if bud.reference == self.name and bud.to_account == acc.budget_expense_account:
						return
					
				budget = self.append('budget_update', {})

				budget.reference = self.name
				budget.transaction_date = self.transaction_date
				budget.budget_change_type = "Initial"
				budget.to_department = self.main_department
				budget.to_account = acc.budget_expense_account
				budget.change_amount = acc.approved_amount

				new_budget = create_budget(self.cost_center, self.fiscal_year, acc.budget_expense_account, acc.net_balance)

				budget.erpnext_budget_reference = new_budget
				self.save(ignore_permissions=True)
				print(budget.erpnext_budget_reference, '-------budget.erpnext_budget_reference------', budget.name)

	def cancel_connected_budget(self):
		for budget in self.budget_update:
			budget_exists=frappe.db.exists('Budget', budget.erpnext_budget_reference)
			if budget_exists:
				doc = frappe.get_doc('Budget', budget.erpnext_budget_reference)
				if doc:
					print(doc.name, '---budget')
					if doc.docstatus == 1:
						doc.cancel()

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_budget_account(doctype, txt, searchfield, start, page_len, filters):
	company = erpnext.get_default_company()
	account_list = frappe.db.get_all("Company",filters={"name":company},
							  fields=BUDGET_EXPENSE_ACCOUNT,as_list=0)

	account_name_list = []
	for acct in account_list:
		for budget_account in BUDGET_EXPENSE_ACCOUNT:
			account_name = (acct.get(budget_account),)
			account_name_list.append(account_name)	

	return account_name_list