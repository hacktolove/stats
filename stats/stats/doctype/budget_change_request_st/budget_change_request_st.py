# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from frappe import _
from stats.api import create_budget
from stats.constants import BUDGET_EXPENSE_ACCOUNT
from stats.budget import get_budget_account_details
from frappe.utils import flt

class BudgetChangeRequestST(Document):

	def validate(self):
		self.set_amount_values()
		self.validate_interal_transfer_amount()
		# self.budget_update_for_enhancement_type()
		# self.budget_update_for_internal_transfer_type()

	def on_submit(self):
		self.budget_update_for_enhancement_type()
		self.budget_update_for_internal_transfer_type()

	def set_amount_values(self):
		if self.enhancement_amount:
			self.to_amount = self.enhancement_amount

		if self.internal_amount:
			self.from_amount = -self.internal_amount
			self.to_amount = self.internal_amount

	def validate_interal_transfer_amount(self):
		if self.budget_change_type == "Internal Transfer":
			from_db_doc = frappe.get_doc("Department Budget ST", {"fiscal_year":self.fiscal_year, "main_department":self.from_main_department})
			acc_details = get_budget_account_details(from_db_doc.cost_center,self.from_account,self.fiscal_year)

			if acc_details:
				self.available_amount = acc_details.available

				if self.internal_amount > acc_details.available:
					frappe.throw(_("You cannot transfer more than {0}").format(self.available_amount))
			else:
				frappe.throw(_("No Budget Found"))
	
	def budget_update_for_enhancement_type(self):
		if self.budget_change_type == "Enhancement":
			print("hello")
			db_doc = frappe.get_doc("Department Budget ST", {"fiscal_year":self.fiscal_year, "main_department":self.to_main_department})
			print(db_doc.name, '-----------------name--------')
			if db_doc:
				for acc in db_doc.account_table:
					if acc.budget_expense_account == self.to_account:
						prev_approved_amt = acc.approved_amount
						net_balance = acc.net_balance
						acc.approved_amount = flt((self.enhancement_amount + prev_approved_amt),2)

						budget_amount = flt((net_balance + self.enhancement_amount),2)
						print(budget_amount, '---------budget_amount')

						budget = db_doc.append("budget_update", {})
						budget.reference = self.name
						budget.transaction_date = self.transaction_date
						budget.budget_change_type = "Enhancement"
						budget.to_department = self.to_main_department
						budget.to_account = self.to_account
						budget.change_amount = self.enhancement_amount

						if len(db_doc.budget_update) > 0:
							cancel_previous_budget_doc(db_doc.fiscal_year, db_doc.cost_center, self.to_account)
							# prev_budget = frappe.get_doc("Budget", db_doc.budget_update[0].erpnext_budget_reference)
							# prev_budget.cancel()
						new_budget = create_budget(db_doc.cost_center, self.fiscal_year, self.to_account, budget_amount)

						budget.erpnext_budget_reference = new_budget
						print(budget.erpnext_budget_reference, '-------budget.erpnext_budget_reference')
						db_doc.save(ignore_permissions=True)

	def budget_update_for_internal_transfer_type(self):
		if self.budget_change_type == "Internal Transfer":
			from_db_doc = frappe.get_doc("Department Budget ST", {"fiscal_year":self.fiscal_year, "main_department":self.from_main_department})
			to_db_doc = frappe.get_doc("Department Budget ST", {"fiscal_year":self.fiscal_year, "main_department":self.to_main_department})

			print(from_db_doc.name, '--from_db_doc')
			print(to_db_doc.name, '----to_db_doc')
			if from_db_doc and to_db_doc:
				for from_acc in from_db_doc.account_table:
					if from_acc.budget_expense_account == self.from_account:
						prev_from_approved_amt = from_acc.approved_amount
						from_net_balance = from_acc.net_balance
						from_acc.approved_amount = flt(((prev_from_approved_amt or 0) - (self.internal_amount or 0)),2)

						from_budget_amount = from_net_balance + self.from_amount

						from_budget = from_db_doc.append("budget_update", {})
						from_budget.reference = self.name
						from_budget.transaction_date = self.transaction_date
						from_budget.budget_change_type = "Internal Transfer"
						from_budget.from_department = self.from_main_department
						from_budget.from_account = self.from_account
						from_budget.to_department = self.to_main_department
						from_budget.to_account = self.to_account
						from_budget.change_amount = self.from_amount

						if len(from_db_doc.budget_update) > 0:
							cancel_previous_budget_doc(from_db_doc.fiscal_year, from_db_doc.cost_center, self.from_account)
						
						from_new_budget = create_budget(from_db_doc.cost_center, self.fiscal_year, self.from_account, from_budget_amount)
						from_budget.erpnext_budget_reference = from_new_budget
						from_db_doc.save(ignore_permissions=True)

				for to_acc in to_db_doc.account_table:
					if to_acc.budget_expense_account == self.to_account:
						prev_to_approved_amt = to_acc.approved_amount
						to_net_balance = to_acc.net_balance
						to_acc.approved_amount = flt(((prev_to_approved_amt or 0) + (self.internal_amount or 0)),2)

						to_budget_amount = to_net_balance + self.to_amount

						to_budget = to_db_doc.append("budget_update", {})
						to_budget.reference = self.name
						to_budget.transaction_date = self.transaction_date
						to_budget.budget_change_type = "Internal Transfer"
						to_budget.from_department = self.from_main_department
						to_budget.from_account = self.from_account
						to_budget.to_department = self.to_main_department
						to_budget.to_account = self.to_account
						to_budget.change_amount = self.to_amount

						if len(to_db_doc.budget_update) > 0:
							cancel_previous_budget_doc(to_db_doc.fiscal_year, to_db_doc.cost_center, self.to_account)
							
						from_new_budget = create_budget(to_db_doc.cost_center, self.fiscal_year, self.to_account, to_budget_amount)
						to_budget.erpnext_budget_reference = from_new_budget
						to_db_doc.save(ignore_permissions=True)

def cancel_previous_budget_doc(fiscal_year, cost_center, account):
	budget_list = frappe.db.get_all("Budget", {"fiscal_year":fiscal_year, "cost_center":cost_center, "docstatus": 1}, ['name'])
	if len(budget_list) > 0:
		for budget in budget_list:
			bud = frappe.get_doc('Budget', budget.name)
			for acc in bud.accounts:
				if acc.account == account:
					print(bud.name, '---budget')
					bud.cancel()

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_budget_account_for_budget_change_request(doctype, txt, searchfield, start, page_len, filters):
	main_department = filters.get('main_department')
	fiscal_year = filters.get('fiscal_year')

	db_list = frappe.db.get_all("Department Budget ST", filters={"main_department":main_department,"fiscal_year":fiscal_year, "docstatus":1}, fields=["name"])
	
	account_name_list = []

	if len(db_list) > 0:
		for db in db_list:
			db_doc = frappe.get_doc("Department Budget ST", db.name)
			for acct in db_doc.account_table:
				participate_in_budget_change_equest = frappe.db.get_value('Account', acct.budget_expense_account, 'custom_acct_not_in_budget_change_request')
				if participate_in_budget_change_equest == 0:
					account_name = (acct.get('budget_expense_account'),)
					account_name_list.append(account_name)
				else:
					continue
		return account_name_list
	else:
		frappe.throw(_("No Department Budget Found"))