# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import get_link_to_form,today
from frappe.model.document import Document


class PaymentRequestST(Document):

	def validate(self):
		total_amount = 0
		if len(self.employees)>0:
			for row in self.employees:
				total_amount = total_amount + (row.amount or 0)
		if not self.total_amount:
			self.total_amount = total_amount

		self.set_party_name_based_on_party_type()

	def set_party_name_based_on_party_type(self):
		if self.party_type and self.party_type == "Employee":
			self.party_name_employee = "Multiple Payment"

	def on_submit(self):
		company = erpnext.get_default_company()
		self.create_payment_procedure_on_submit_of_payment_request()
		if self.reference_name == "Business Trip Sheet ST":
			company_business_trip_budget_expense_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_expense_account")
			company_business_trip_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_chargeable_account")
			self.create_journal_entry_on_submit_of_payment_request(company_business_trip_budget_expense_account,company_business_trip_budget_chargeable_account)

		elif self.reference_name == "Employee Reallocation Sheet ST":
			company_reallocation_budget_expense_account = frappe.db.get_value("Company",company,"custom_reallocation_budget_expense_account")
			company_reallocation_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_reallocation_budget_chargeable_account")
			self.create_journal_entry_on_submit_of_payment_request(company_reallocation_budget_expense_account,company_reallocation_budget_chargeable_account)

		elif self.reference_name == "Overtime Sheet ST":
			company_overtime_budget_expense_account = frappe.db.get_value("Company",company,"custom_overtime_budget_expense_account")
			company_overtime_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_overtime_budget_chargeable_account")
			self.create_journal_entry_on_submit_of_payment_request(company_overtime_budget_expense_account,company_overtime_budget_chargeable_account)
		
		# elif self.reference_name == "Petty Cash Request ST":
		# 	self.create_journal_entry_for_petty_cash()

		elif self.reference_name == "Achievement Certificate ST":
			self.create_jv_for_achievement_certificate()
		
		elif self.reference_name == "Employee Annual Reward ST":
			company_annual_reward_expense_account = frappe.db.get_value("Company",company,"custom_annual_reward_expense_account")
			company_annual_reward_chargeable_account = frappe.db.get_value("Company",company,"custom_annual_reward_chargeable_account")
			self.create_journal_entry_on_submit_of_payment_request(company_annual_reward_expense_account,company_annual_reward_chargeable_account)
		
		elif self.reference_name == "End Of Service Sheet ST":
			company_default_end_of_service_allocated_account = frappe.db.get_value("Company",company,"custom_default_end_of_service_allocated_account")
			self.create_journal_entry_for_end_of_service_and_vacation_encasement(company_default_end_of_service_allocated_account)
		
		elif self.reference_name == "Vacation Encashment Sheet ST":
			company_default_vacation_allocated_account = frappe.db.get_value("Company",company,"custom_default_vacation_allocated_account")
			self.create_journal_entry_for_end_of_service_and_vacation_encasement(company_default_vacation_allocated_account)
		
		elif self.reference_name == "Education Allowance Sheet ST":
			company_education_allowance_expense_account = frappe.db.get_value("Company",company,"custom_education_allowance_expense_account")
			company_education_allowance_chargeable_account_ = frappe.db.get_value("Company",company,"custom_education_allowance_chargeable_account_")
			self.create_journal_entry_on_submit_of_payment_request(company_education_allowance_expense_account,company_education_allowance_chargeable_account_)

		if self.type == _("Unclassified"):
			self.create_journal_entry_on_submit_of_payment_request_for_unclassified(self.default_expense_account,self.default_chargeable_account)

	def create_journal_entry_on_submit_of_payment_request(self,company_budget_expense_account,company_budget_chargeable_account):
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.transaction_date
		je.custom_payment_request_reference = self.name
		
		accounts = []
		employee_detais = frappe.db.sql("""
				SELECT
				main_department,
				SUM(amount) as amount
			FROM
				`tabEmployee Details For Payment ST`
			WHERE
				parent = %s
			GROUP By
				main_department
		""",self.name,as_dict=1,debug=1)
		print(employee_detais,"employee_detais")

		employee_total_amount = 0
		company = erpnext.get_default_company()
		if len(employee_detais)>0:
			# company_business_trip_budget_expense_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_expense_account")
			# company_business_trip_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_chargeable_account")
			company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")
			for detail_row in employee_detais:
				employee_total_amount = employee_total_amount + detail_row.amount
				department_cost_center = frappe.db.get_value("Department",detail_row.main_department,"custom_department_cost_center")
				accounts_row = {
					"account":company_budget_expense_account,
					"cost_center":department_cost_center,
					"department":detail_row.main_department,
					"debit_in_account_currency":detail_row.amount,
				}
				accounts.append(accounts_row)

			accounts_row_2 = {
					"account":company_budget_chargeable_account,
					"cost_center":company_default_cost_center,
					"department":detail_row.main_department,
					"credit_in_account_currency":employee_total_amount,
			}
			accounts.append(accounts_row_2)
		je.set("accounts",accounts)
		je.run_method('set_missing_values')
		je.save(ignore_permissions=True)
		je.submit()
		frappe.msgprint(_("Journal Entry Due Expense is created from Payment Request {0}").format(get_link_to_form("Journal Entry",je.name)),alert=1)
		
		# Second JV from PR
		company_default_debit_account_mof = frappe.db.get_value("Company",company,"custom_default_debit_account_mof")
		company_default_revenue_account = frappe.db.get_value("Company",company,"custom_default_revenue_account")

		payment_je_doc = frappe.new_doc("Journal Entry")
		payment_je_doc.voucher_type = "Journal Entry"
		payment_je_doc.posting_date = self.transaction_date
		payment_je_doc.custom_payment_request_reference = self.name

		jv_accounts = []

		company = erpnext.get_default_company()
		company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")

		employee_info = frappe.db.sql("""
				SELECT
				main_department,
				SUM(amount) as amount
			FROM
				`tabEmployee Details For Payment ST`
			WHERE
				parent = %s
			GROUP By
				main_department
		""",self.name,as_dict=1,debug=1)
		print(employee_info,"employee_info")

		accounts_row = {
					"account":company_default_debit_account_mof,
					"cost_center":company_default_cost_center,
					"debit_in_account_currency":employee_total_amount,
				}
		jv_accounts.append(accounts_row)

		if len(employee_detais)>0:
			for row in employee_info:
				department_cost_center = frappe.db.get_value("Department",row.main_department,"custom_department_cost_center")
				accounts_row_2 = {
					"account":company_default_revenue_account,
					"cost_center":department_cost_center,
					"department":row.main_department,
					"credit_in_account_currency":row.amount,
				}
				jv_accounts.append(accounts_row_2)

		payment_je_doc.set("accounts",jv_accounts)
		payment_je_doc.run_method('set_missing_values')
		payment_je_doc.save(ignore_permissions=True)
		payment_je_doc.submit()

		frappe.msgprint(_("Journal Entry Due Expense is created from Payment Request {0}").format(get_link_to_form("Journal Entry",payment_je_doc.name)),alert=1)
		
	def create_payment_procedure_on_submit_of_payment_request(self):
		pp_doc = frappe.new_doc("Payment Procedure ST")
		pp_doc.payment_request_reference = self.name
		pp_doc.budget_account = self.budget_account
		pp_doc.party_type = self.party_type
		pp_doc.type = self.type
		if self.type == _("Classified"):
			pp_doc.reference_name = self.reference_name
			pp_doc.reference_no = self.reference_no
		elif self.type == _("Unclassified"):
			pp_doc.default_expense_account = self.default_expense_account
			pp_doc.default_chargeable_account = self.default_chargeable_account
			pp_doc.cost_center = self.cost_center
		pp_doc.total_amount = self.total_amount

		if self.party_type == "Supplier":
			pp_doc.party_name_supplier = self.party_name_supplier
		
		if self.reference_name in ["End Of Service Sheet ST","Vacation Encashment Sheet ST","Purchase Invoice"]:
			pp_doc.payment_type = "Direct"

		if len(self.employees)>0:
			for row in self.employees:
				pp_row = pp_doc.append("employees",{})
				pp_row.employee_no = row.employee_no
				pp_row.amount = row.amount

		pp_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Procedure {0} is created").format(get_link_to_form("Payment Procedure ST", pp_doc.name)),alert=1)

	def create_journal_entry_for_petty_cash(self):

		pc_request_doc = frappe.get_doc("Petty Cash Request ST",self.reference_no)
		department_cost_center = frappe.db.get_value("Department",pc_request_doc.main_department,"custom_department_cost_center")

		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.transaction_date
		je.custom_payment_request_reference = self.name
		
		accounts = []
		company = erpnext.get_default_company()
		company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")
		company_default_employee_petty_cash_account = frappe.db.get_value("Company",company,"custom_default_employee_petty_cash_account")
		
		if len(pc_request_doc.pc_request_account_details)>0:
			for row in pc_request_doc.pc_request_account_details:
				accounts_row = {
					"account":row.account_name,
					"cost_center":department_cost_center,
					"department":pc_request_doc.main_department,
					"debit_in_account_currency":row.amount,
				}
				accounts.append(accounts_row)
		if len(self.employees)>0:
			for row in self.employees:
				accounts_row_2 = {
						"account":company_default_employee_petty_cash_account,
						"cost_center":company_default_cost_center,
						"credit_in_account_currency":self.total_amount,
						"party_type":self.party_type,
						"party":row.employee_no
				}
				accounts.append(accounts_row_2)

		je.set("accounts",accounts)
		je.run_method('set_missing_values')
		je.save(ignore_permissions=True)
		je.submit()
		frappe.msgprint(_("Journal Entry for Petty Cash Request is created from Payment Request {0}").format(get_link_to_form("Journal Entry",je.name)),alert=1)

		# 2nd JV for Petty Cash Request

		company_default_debit_account_mof = frappe.db.get_value("Company",company,"custom_default_debit_account_mof")
		company_default_revenue_account = frappe.db.get_value("Company",company,"custom_default_revenue_account")

		payment_je_doc = frappe.new_doc("Journal Entry")
		payment_je_doc.voucher_type = "Journal Entry"
		payment_je_doc.posting_date = self.transaction_date
		payment_je_doc.custom_payment_request_reference = self.name

		jv_accounts = []
		accounts_row = {
					"account":company_default_debit_account_mof,
					"cost_center":company_default_cost_center,
					"debit_in_account_currency":self.total_amount,
				}
		jv_accounts.append(accounts_row)

		if len(self.employees)>0:
			for row in self.employees:
				accounts_row_2 = {
					"account":company_default_revenue_account,
					"cost_center":department_cost_center,
					"department":pc_request_doc.main_department,
					"credit_in_account_currency":self.total_amount,
				}
				jv_accounts.append(accounts_row_2)

		payment_je_doc.set("accounts",jv_accounts)
		payment_je_doc.run_method('set_missing_values')
		payment_je_doc.save(ignore_permissions=True)
		payment_je_doc.submit()

		frappe.msgprint(_("Journal Entry for Petty Cash Request is created from Payment Request {0}").format(get_link_to_form("Journal Entry",payment_je_doc.name)),alert=1)
	
	def create_jv_for_achievement_certificate(self):
		certificate_doc = frappe.get_doc("Achievement Certificate ST",self.reference_no)
		department_cost_center = frappe.db.get_value("Department",certificate_doc.department_request,"custom_department_cost_center")

		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.transaction_date
		je.custom_payment_request_reference = self.name
		
		accounts = []
		company = erpnext.get_default_company()
		company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")
		custom_default_international_subscription_expense_account = frappe.db.get_value("Company",company,"custom_default_international_subscription_expense_account")
		custom_default_international_subscription_chargeable_account = frappe.db.get_value("Company",company,"custom_default_international_subscription_chargeable_account")
		custom_penalty_income_account = frappe.db.get_value("Company",company,"custom_penalty_income_account")
		if not custom_penalty_income_account:
			frappe.throw(_("Please set Penalty Income Account in {0}").format(get_link_to_form("Company",company)))
		penalty_amount = certificate_doc.penalty_amount or 0
		accounts_row_penalty = {}

		if certificate_doc.reference_type == "International Subscription Payment Request ST":
			if penalty_amount > 0:
				accounts_row = {
					"account":custom_default_international_subscription_expense_account,
					"cost_center":department_cost_center,
					"department":certificate_doc.department_request,
					"debit_in_account_currency":self.total_amount + penalty_amount,
				}
				accounts_row_penalty = {
					"account":custom_penalty_income_account,
					"cost_center":company_default_cost_center,
					"credit_in_account_currency":penalty_amount,
				}
				accounts.append(accounts_row)
				accounts.append(accounts_row_penalty)

				accounts_row_2 = {
						"account":custom_default_international_subscription_chargeable_account,
						"cost_center":company_default_cost_center,
						"credit_in_account_currency":self.total_amount
						}
				accounts.append(accounts_row_2)
			else :
				accounts_row = {
					"account":custom_default_international_subscription_expense_account,
					"cost_center":department_cost_center,
					"department":certificate_doc.department_request,
					"debit_in_account_currency":self.total_amount,
					}
				accounts.append(accounts_row)

				accounts_row_2 = {
						"account":custom_default_international_subscription_chargeable_account,
						"cost_center":company_default_cost_center,
						"credit_in_account_currency":self.total_amount
						}
				accounts.append(accounts_row_2)
		
		elif certificate_doc.reference_type in ["Purchase Order","Purchase Invoice"]:
			chargeable_account = frappe.db.get_value("Company",company,"default_payable_account")
			if certificate_doc.reference_type == "Purchase Order":
				expense_account = frappe.db.get_value("Purchase Order Item",{"parent":certificate_doc.invoice_reference},"expense_account")
			else :
				expense_account = frappe.db.get_value("Purchase Invoice Item",{"parent":certificate_doc.invoice_reference},"expense_account")
			print(expense_account,"expense account-----------------------------")
			if penalty_amount > 0:
				accounts_row = {
					"account":expense_account,
					"cost_center":department_cost_center,
					"department":certificate_doc.department_request,
					"debit_in_account_currency":self.total_amount + penalty_amount,
				}
				accounts_row_penalty = {
					"account":custom_penalty_income_account,
					"cost_center":company_default_cost_center,
					"credit_in_account_currency":penalty_amount,
				}
				accounts.append(accounts_row)
				accounts.append(accounts_row_penalty)

				accounts_row_2 = {
						"account":chargeable_account,
						"cost_center":company_default_cost_center,
						"credit_in_account_currency":self.total_amount,
						"party_type":self.party_type,
						"party":self.party_name_supplier
				}
				accounts.append(accounts_row_2)
			else :
				accounts_row = {
					"account":expense_account,
					"cost_center":department_cost_center,
					"department":certificate_doc.department_request,
					"debit_in_account_currency":self.total_amount,
				}
				accounts.append(accounts_row)

				accounts_row_2 = {
								"account":chargeable_account,
								"cost_center":company_default_cost_center,
								"credit_in_account_currency":self.total_amount,
								"party_type":self.party_type,
								"party":self.party_name_supplier
						}
				accounts.append(accounts_row_2)

		je.set("accounts",accounts)
		je.run_method('set_missing_values')
		je.save(ignore_permissions=True)
		je.submit()
		frappe.msgprint(_("Journal Entry for Achievement Certificate is created from Payment Request {0}").format(get_link_to_form("Journal Entry",je.name)),alert=1)

		# 2nd JV for Achievement Certificate

		je_doc = frappe.new_doc("Journal Entry")
		je_doc.voucher_type = "Journal Entry"
		je_doc.posting_date = self.transaction_date
		je_doc.custom_payment_request_reference = self.name
		
		jv_accounts = []
		company = erpnext.get_default_company()
		company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")
		company_default_debit_account_mof = frappe.db.get_value("Company",company,"custom_default_debit_account_mof")
		company_default_revenue_account = frappe.db.get_value("Company",company,"custom_default_revenue_account")

		accounts_row = {
					"account":company_default_debit_account_mof,
					"cost_center":company_default_cost_center,
					"debit_in_account_currency":self.total_amount,
				}
		jv_accounts.append(accounts_row)

		accounts_row_2 = {
						"account":company_default_revenue_account,
						"cost_center":department_cost_center,
						"credit_in_account_currency":self.total_amount
				}
		jv_accounts.append(accounts_row_2)

		je_doc.set("accounts",jv_accounts)
		je_doc.run_method('set_missing_values')
		je_doc.save(ignore_permissions=True)
		je_doc.submit()
		frappe.msgprint(_("Journal Entry for Achievement Certificate is created from Payment Request {0}").format(get_link_to_form("Journal Entry",je_doc.name)),alert=1)

	def create_journal_entry_for_end_of_service_and_vacation_encasement(self,allocated_account):
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.transaction_date
		je.custom_payment_request_reference = self.name
		
		company = erpnext.get_default_company()
		company_default_payment_order_account = frappe.db.get_value("Company",company,"custom_default_payment_order_account")
		accounts = []
		company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")
		accounts_row = {
			"account":allocated_account,
			"cost_center":company_default_cost_center,
			"debit_in_account_currency":self.total_amount,
		}
		accounts.append(accounts_row)

		accounts_row_2 = {
				"account":company_default_payment_order_account,
				"cost_center":company_default_cost_center,
				"credit_in_account_currency":self.total_amount,
		}
		accounts.append(accounts_row_2)
		je.set("accounts",accounts)
		je.run_method('set_missing_values')
		je.save(ignore_permissions=True)
		je.submit()
		frappe.msgprint(_("Journal Entry Due Expense is created from Payment Request {0}").format(get_link_to_form("Journal Entry",je.name)),alert=1)
		
		# Second JV from PR
		company_default_debit_account_mof = frappe.db.get_value("Company",company,"custom_default_debit_account_mof")
		company_default_revenue_account = frappe.db.get_value("Company",company,"custom_default_revenue_account")

		payment_je_doc = frappe.new_doc("Journal Entry")
		payment_je_doc.voucher_type = "Journal Entry"
		payment_je_doc.posting_date = self.transaction_date
		payment_je_doc.custom_payment_request_reference = self.name

		jv_accounts = []

		company = erpnext.get_default_company()
		company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")

		employee_info = frappe.db.sql("""
				SELECT
				main_department,
				SUM(amount) as amount
			FROM
				`tabEmployee Details For Payment ST`
			WHERE
				parent = %s
			GROUP By
				main_department
		""",self.name,as_dict=1,debug=1)
		print(employee_info,"employee_info")

		accounts_row = {
					"account":company_default_debit_account_mof,
					"cost_center":company_default_cost_center,
					"debit_in_account_currency":self.total_amount,
				}
		jv_accounts.append(accounts_row)

		if len(employee_info)>0:
			for row in employee_info:
				department_cost_center = frappe.db.get_value("Department",row.main_department,"custom_department_cost_center")
				accounts_row_2 = {
					"account":company_default_revenue_account,
					"cost_center":department_cost_center,
					"department":row.main_department,
					"credit_in_account_currency":row.amount,
				}
				jv_accounts.append(accounts_row_2)

		payment_je_doc.set("accounts",jv_accounts)
		payment_je_doc.run_method('set_missing_values')
		payment_je_doc.save(ignore_permissions=True)
		payment_je_doc.submit()

		frappe.msgprint(_("Journal Entry Due Expense is created from Payment Request {0}").format(get_link_to_form("Journal Entry",payment_je_doc.name)),alert=1)
	
	def create_journal_entry_on_submit_of_payment_request_for_unclassified(self,default_expense_account,default_chargeable_account):
		company = erpnext.get_default_company()

		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.transaction_date
		je.custom_payment_request_reference = self.name
		
		accounts = []
		
		accounts_row = {
			"account":default_expense_account,
			"cost_center":self.cost_center,
			"debit_in_account_currency":self.total_amount,
		}
		accounts.append(accounts_row)

		accounts_row_2 = {
				"account":default_chargeable_account,
				"cost_center":self.cost_center,
				"credit_in_account_currency":self.total_amount,
		}
		accounts.append(accounts_row_2)
		je.set("accounts",accounts)
		je.run_method('set_missing_values')
		je.save(ignore_permissions=True)
		je.submit()
		frappe.msgprint(_("Journal Entry Due Expense is created from Payment Request {0}").format(get_link_to_form("Journal Entry",je.name)),alert=1)
		
		# Second JV from PR
		company_default_debit_account_mof = frappe.db.get_value("Company",company,"custom_default_debit_account_mof")
		company_default_revenue_account = frappe.db.get_value("Company",company,"custom_default_revenue_account")

		payment_je_doc = frappe.new_doc("Journal Entry")
		payment_je_doc.voucher_type = "Journal Entry"
		payment_je_doc.posting_date = self.transaction_date
		payment_je_doc.custom_payment_request_reference = self.name

		jv_accounts = []

		accounts_row = {
					"account":company_default_debit_account_mof,
					"cost_center":self.cost_center,
					"debit_in_account_currency":self.total_amount,
				}
		jv_accounts.append(accounts_row)

		accounts_row_2 = {
			"account":company_default_revenue_account,
			"cost_center":self.cost_center,
			"credit_in_account_currency":self.total_amount,
		}
		jv_accounts.append(accounts_row_2)

		payment_je_doc.set("accounts",jv_accounts)
		payment_je_doc.run_method('set_missing_values')
		payment_je_doc.save(ignore_permissions=True)
		payment_je_doc.submit()

		frappe.msgprint(_("Journal Entry Due Expense is created from Payment Request {0}").format(get_link_to_form("Journal Entry",payment_je_doc.name)),alert=1)