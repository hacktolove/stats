# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class POPaymentScheduleST(Document):
	def validate(self):
		self.calculate_and_validate_amount()

	def calculate_and_validate_amount(self):
		po_amount = frappe.db.get_value("Purchase Order", self.po_reference, "grand_total")
		total_amount = 0
		unique_accounts = []
		if len(self.payment_details) > 0:
			for row in self.payment_details:
				row.percentage = row.payment_value / po_amount * 100
				total_amount += row.payment_value or 0
				if row.budget_account not in unique_accounts:
					unique_accounts.append(row.budget_account)
				
			if total_amount > po_amount:
				frappe.throw("Total amount cannot be greater than {0}".format(po_amount))
			
			if len(unique_accounts) > 0:
				for account in unique_accounts:
					total_payment_amount = 0
					expense_account_amount = frappe.db.get_all("Purchase Order Item", filters={"parent": self.po_reference, "expense_account": account}, fields=["sum(amount) as total_amount"])
					for row in self.payment_details:
						if row.budget_account == account:
							total_payment_amount += row.payment_value or 0
					if total_payment_amount > expense_account_amount[0].total_amount:
						frappe.throw("Total amount for account {0} cannot be greater than {1}".format(frappe.bold(account), frappe.bold(expense_account_amount[0].total_amount)))
		
		self.total_amount = total_amount
