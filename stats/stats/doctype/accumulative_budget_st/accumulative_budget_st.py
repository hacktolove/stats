# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, floor

class AccumulativeBudgetST(Document):
	def validate(self):
			self.calculate_amount_difference_and_total_amount()
			self.validate_approved_amount_in_budget_allocation()
			# self.set_approved_amount_in_department_budget()
	
	def on_submit(self):
		self.set_approved_amount_in_department_budget()

	def calculate_amount_difference_and_total_amount(self):
		total_requested_amount = 0
		total_approved_amount = 0
		if len(self.account_details) > 0:
			for row in self.account_details:
				row.difference = flt(((row.total_requested_amount or 0) - (row.total_approved_amount or 0)),2)
				total_requested_amount = total_requested_amount + (row.total_requested_amount or 0)
				total_approved_amount = total_approved_amount + (row.total_approved_amount or 0)

		self.total_requested_amount = total_requested_amount
		self.total_approved_amount = total_approved_amount

	def set_approved_amount_in_department_budget(self):
		if len(self.department_wise_budget_allocation_details) > 0:

			department_budget = []
			for row in self.department_wise_budget_allocation_details:
				# db_doc = frappe.get_doc('Accounts Details ST', row.department_acct_details_name)
				# # print(db_doc.approved_amount,'-----before----')
				# db_doc.approved_amount = row.approved_amount


				# db_doc.save(ignore_permissions=True)
				# print(db_doc.approved_amount, '----after----')
				frappe.db.set_value('Accounts Details ST', row.department_acct_details_name, 'approved_amount', row.approved_amount)
				department_budget.append(row.department_budget_name)
				# doc = frappe.get_doc('Department Budget ST', row.department_budget_name)
				# doc.allocated_amount = row.approved_amount
				# doc.save(ignore_permissions=True)
				# frappe.db.set_value('Department Budget ST', row.department_budget_name, 'allocated_amount', row.approved_amount)
				frappe.msgprint(_("In Department Budget {0} approved amount set.")
					.format(row.department_budget_name), alert=1)
				
			if len(department_budget) > 0:
				for dep in department_budget:
					doc = frappe.get_doc('Department Budget ST', dep)
					doc.save(ignore_permissions=True)
				
	def validate_approved_amount_in_budget_allocation(self):
		if len(self.account_details) > 0:
			for ad in self.account_details:
				total_approved_amount = 0
				if len(self.department_wise_budget_allocation_details) > 0:
					for row in self.department_wise_budget_allocation_details:
						if ad.budget_expense_account == row.budget_expense_account:
							total_approved_amount = total_approved_amount + row.approved_amount

					if ad.total_approved_amount and total_approved_amount > ad.total_approved_amount:
						frappe.throw(_("For Account {0}: Allocated Approved Amount {1} cannot be greater than Total approved amount {2}").format(ad.budget_expense_account,total_approved_amount, ad.total_approved_amount))

	@frappe.whitelist()
	def get_department_budget_requests(self):
		fetch_accumulative_budget_request = frappe.db.sql("""SELECT	ad.budget_expense_account, sum(ad.requested_amount) as total_requested_amount, ad.budget_type, ad.economic_number, ad.classifications
													FROM `tabAccounts Details ST` AS ad 
													inner join `tabDepartment Budget ST` AS db on db.name = ad.parent 
													where db.fiscal_year = %s and db.docstatus = 1 
													group by ad.budget_expense_account""",self.fiscal_year,as_dict=True)
		return fetch_accumulative_budget_request
	
	@frappe.whitelist()
	def get_department_wise_budegt_allocation(self):
		accumulative_budget_request=self.account_details
		department_and_account_budget_requests=self.get_department_and_account_budget_requests()

		for budget_amount in department_and_account_budget_requests:
			for acct_amount in accumulative_budget_request:
				if acct_amount.total_approved_amount <= 0:
					frappe.throw(_('Approved amount should ne greater than zero in {0} row').format(acct_amount.idx))
				if budget_amount['budget_expense_account']==acct_amount.budget_expense_account:
					budget_amount['total_requested_amount']=acct_amount.total_requested_amount
					budget_amount['approved_amount']= floor((budget_amount['requested_amount']/acct_amount.total_requested_amount)*acct_amount.total_approved_amount)
					break
		return department_and_account_budget_requests


	@frappe.whitelist()
	def get_department_and_account_budget_requests(self):
		department_and_account_budget_requests = frappe.db.sql("""SELECT
					db.name as department_budget_name ,db.main_department ,
					ad.name as department_acct_details_name ,ad.budget_expense_account,
					0 as total_requested_amount, ad.requested_amount , 0 as approved_amount
				FROM
					`tabAccounts Details ST` ad
				inner join `tabDepartment Budget ST` db on
					db.name = ad.parent
				where db.fiscal_year = %s and db.docstatus = 1 """,self.fiscal_year,as_dict=True)
		return department_and_account_budget_requests	