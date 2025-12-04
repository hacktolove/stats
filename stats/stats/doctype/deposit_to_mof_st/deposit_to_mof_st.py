# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document


class DepositToMOFST(Document):

	def on_submit(self):
		self.validate_attachment()
		self.create_jv_for_depofit_to_mof()
		self.change_status_of_pc_repayment()

	def validate_attachment(self):
		if not self.payment_proof_attachment:
			frappe.throw(_("Please attach payment proof"))
		
	def create_jv_for_depofit_to_mof(self):

		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.creation_date
		je.custom_deposit_to_mof_reference = self.name
		
		accounts = []
		company = erpnext.get_default_company()
		company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")
		company_default_bank_account = frappe.db.get_value("Company",company,"default_bank_account")
		company_default_central_bank_account = frappe.db.get_value("Company",company,"custom_default_central_bank_account")
		
		accounts_row = {
			"account":company_default_central_bank_account,
			"cost_center":company_default_cost_center,
			"debit_in_account_currency":self.total_unpaid,
		}
		accounts.append(accounts_row)

		accounts_row_2 = {
			"account":company_default_bank_account,
			"cost_center":company_default_cost_center,
			"credit_in_account_currency":self.total_unpaid
		}
		accounts.append(accounts_row_2)

		je.set("accounts",accounts)
		je.run_method('set_missing_values')
		je.save(ignore_permissions=True)
		je.submit()
		frappe.msgprint(_("Journal Entry is created {0}").format(get_link_to_form("Journal Entry",je.name)),alert=1)

	def change_status_of_pc_repayment(self):
		pc_repayment_doc = frappe.get_doc("Petty Cash Re-Payment ST",self.petty_cash_repayment_reference)
		pc_repayment_doc.deposit_to_mof = "Done"
		pc_repayment_doc.add_comment("Comment",text="Status changed to Done due to Deposit to MOF {0}".format(get_link_to_form("Deposit To MOF ST",self.name)))
		pc_repayment_doc.save(ignore_permissions=True)
		frappe.msgprint(_("PC Re Payment status changed to <b>Done</b>"),alert=True)		