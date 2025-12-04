# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form,today
from stats.api import create_payment_journal_entry_from_payment_procedure, create_journal_entry_for_petty_cash


class PaymentProcedureST(Document):

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
		if not self.payment_type:
			frappe.throw(_("Please select payment type"))

		if self.reference_name in ["End Of Service Sheet ST","Vacation Encashment Sheet ST"]:
			if self.payment_type == _("Indirect Payment"):
				frappe.throw(_("You cannot select payment type Indirect Payment"))
		
		total_employee_amount = 0
		if len(self.employees)>0:
			for row in self.employees:
				total_employee_amount = total_employee_amount + (row.amount or 0)

		company = erpnext.get_default_company()
		if self.payment_request_reference:
			company_default_central_bank_account = frappe.db.get_value("Company",company,"custom_default_central_bank_account")
			company_default_payment_order_account = frappe.db.get_value("Company",company,"custom_default_payment_order_account")
			company_default_debit_account_mof = frappe.db.get_value("Company",company,"custom_default_debit_account_mof")
			company_default_pending_income_account = frappe.db.get_value("Company",company,"custom_default_pending_income_account")
			company_default_bank_account = frappe.db.get_value("Company",company,"default_bank_account")
			

			if self.payment_type == _("Indirect Payment"):
				je_date = self.bank_enhancement_date
			else :
				je_date = self.transaction_date
			
			if self.type == _("Classified"):
				if self.reference_name not in ["End Of Service Sheet ST","Vacation Encashment Sheet ST","Purchase Invoice","Petty Cash Request ST"]:
					create_payment_journal_entry_from_payment_procedure(self,company_default_payment_order_account,company_default_debit_account_mof,self.total_amount,je_date)

				if self.reference_name == "Business Trip Sheet ST":
					company_business_trip_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_chargeable_account")
					if self.payment_type == _("Direct Payment"):
						create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.transaction_date)
						create_payment_journal_entry_from_payment_procedure(self,company_business_trip_budget_chargeable_account,company_default_central_bank_account,total_employee_amount,je_date=today())

					elif self.payment_type == _("Indirect Payment"):
						if self.middle_bank_account:
							create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.bank_enhancement_date)
							create_payment_journal_entry_from_payment_procedure(self,company_business_trip_budget_chargeable_account,self.middle_bank_account,total_employee_amount,je_date=today())

				elif self.reference_name == "Employee Reallocation Sheet ST":
					company_reallocation_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_reallocation_budget_chargeable_account")
					if self.payment_type == _("Direct Payment"):
						create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.transaction_date)
						create_payment_journal_entry_from_payment_procedure(self,company_reallocation_budget_chargeable_account,company_default_central_bank_account,total_employee_amount,je_date=today())
					elif self.payment_type == _("Indirect Payment"):
						if self.middle_bank_account:
							create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.bank_enhancement_date)
							create_payment_journal_entry_from_payment_procedure(self,company_reallocation_budget_chargeable_account,self.middle_bank_account,total_employee_amount,je_date=today())
				
				elif self.reference_name == "Overtime Sheet ST":
					company_overtime_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_overtime_budget_chargeable_account")
					if self.payment_type == _("Direct Payment"):
						create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.transaction_date)
						create_payment_journal_entry_from_payment_procedure(self,company_overtime_budget_chargeable_account,company_default_central_bank_account,total_employee_amount,je_date=today())
					elif self.payment_type == _("Indirect Payment"):
						if self.middle_bank_account:
							create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.bank_enhancement_date)
							create_payment_journal_entry_from_payment_procedure(self,company_overtime_budget_chargeable_account,self.middle_bank_account,total_employee_amount,je_date=today())

				elif self.reference_name == "Petty Cash Request ST":
					company_default_employee_petty_cash_account = frappe.db.get_value("Company",company,"custom_default_employee_petty_cash_account")
					if self.payment_type == _("Direct Payment"):
						# create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.transaction_date)
						if len(self.employees)>0:
							for row in self.employees:
								create_journal_entry_for_petty_cash(self,company_default_employee_petty_cash_account,company_default_payment_order_account,total_employee_amount,row.main_department,je_date=None,party_type=self.party_type,party_name=row.employee_no,jv_type="Procedure")
								create_journal_entry_for_petty_cash(self,company_default_payment_order_account,company_default_bank_account,total_employee_amount,row.main_department,je_date=None,party_type=self.party_type,party_name=row.employee_no,jv_type="Procedure")
								create_journal_entry_for_petty_cash(self,company_default_bank_account,company_default_debit_account_mof,total_employee_amount,row.main_department,je_date=None,party_type=self.party_type,party_name=row.employee_no,jv_type="Procedure")
								create_journal_entry_for_petty_cash(self,company_default_debit_account_mof,company_default_pending_income_account,total_employee_amount,row.main_department,je_date=None,party_type=self.party_type,party_name=row.employee_no,jv_type="Procedure")
								# create_payment_journal_entry_from_payment_procedure(self,company_default_employee_petty_cash_account,company_default_payment_order_account,total_employee_amount,je_date=today(),party_type=self.party_type,party_name=row.employee_no)
								# create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,total_employee_amount,je_date=today(),party_type=self.party_type,party_name=row.employee_no)
					elif self.payment_type == _("Indirect Payment"):
						if self.middle_bank_account:
							# create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.bank_enhancement_date)
							if len(self.employees)>0:
								for row in self.employees:
									create_journal_entry_for_petty_cash(self,company_default_employee_petty_cash_account,company_default_payment_order_account,total_employee_amount,row.main_department,je_date=None,party_type=self.party_type,party_name=row.employee_no,jv_type="Procedure")
									create_journal_entry_for_petty_cash(self,company_default_payment_order_account,self.middle_bank_account,total_employee_amount,row.main_department,je_date=None,party_type=self.party_type,party_name=row.employee_no,jv_type="Procedure")
									create_journal_entry_for_petty_cash(self,self.middle_bank_account,company_default_debit_account_mof,total_employee_amount,row.main_department,je_date=None,party_type=self.party_type,party_name=row.employee_no,jv_type="Procedure")
									create_journal_entry_for_petty_cash(self,company_default_debit_account_mof,company_default_pending_income_account,total_employee_amount,row.main_department,je_date=None,party_type=self.party_type,party_name=row.employee_no,jv_type="Procedure")
									# create_payment_journal_entry_from_payment_procedure(self,company_default_employee_petty_cash_account,self.middle_bank_account,total_employee_amount,je_date=today(),party_type=self.party_type,party_name=row.employee_no)
					pc_request_doc = frappe.get_doc("Petty Cash Request ST",self.reference_no)
					pc_request_doc.payment_status = "Paid"
					pc_request_doc.add_comment("Comment", text="Payment Status changed to Paid due to {0}".format(get_link_to_form("Payment Procedure ST",self.name)))
					pc_request_doc.save(ignore_permissions=True)
					frappe.msgprint(_("PC Request {0} payment status changed to <b>Paid</b>".format(get_link_to_form("Petty Cash Request ST",self.reference_no))),alert=True)
					
				elif self.reference_name == "Achievement Certificate ST":
					company_default_international_subscription_chargeable_account = frappe.db.get_value("Company",company,"custom_default_international_subscription_chargeable_account")
					default_payable_account = frappe.db.get_value("Company",company,"default_payable_account")
					document_type = frappe.db.get_value(self.reference_name,self.reference_no,"reference_type")
					if document_type in ["Purchase Order","Purchase Invoice"]:
						chargeable_account = default_payable_account
					elif document_type == "International Subscription Payment Request ST":
						chargeable_account = company_default_international_subscription_chargeable_account
					if self.payment_type == _("Direct Payment"):
						create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.transaction_date)
						create_payment_journal_entry_from_payment_procedure(self,chargeable_account,company_default_central_bank_account,self.total_amount,je_date=today(),party_type=self.party_type,party_name=self.party_name_supplier)
					elif self.payment_type == _("Indirect Payment"):
						if self.middle_bank_account:
							create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.bank_enhancement_date)
							create_payment_journal_entry_from_payment_procedure(self,chargeable_account,self.middle_bank_account,self.total_amount,je_date=today(),party_type=self.party_type,party_name=self.party_name_supplier)

				elif self.reference_name == "Employee Annual Reward ST":
					company_annual_reward_chargeable_account = frappe.db.get_value("Company",company,"custom_annual_reward_chargeable_account")
					if self.payment_type == _("Direct Payment"):
						create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.transaction_date)
						create_payment_journal_entry_from_payment_procedure(self,company_annual_reward_chargeable_account,company_default_central_bank_account,self.total_amount,je_date=today())
					elif self.payment_type == _("Indirect Payment"):
						if self.middle_bank_account:
							create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.bank_enhancement_date)
							create_payment_journal_entry_from_payment_procedure(self,company_annual_reward_chargeable_account,self.middle_bank_account,self.total_amount,je_date=today())
				
				elif self.reference_name == "End Of Service Sheet ST":
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_debit_account_mof,self.total_amount,je_date=self.transaction_date)
					create_payment_journal_entry_from_payment_procedure(self,company_default_payment_order_account,company_default_central_bank_account,self.total_amount,je_date=today())
				
				elif self.reference_name == "Vacation Encashment Sheet ST":
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_debit_account_mof,self.total_amount,je_date=self.transaction_date)
					create_payment_journal_entry_from_payment_procedure(self,company_default_payment_order_account,company_default_central_bank_account,self.total_amount,je_date=today())
				
				elif self.reference_name == "Education Allowance Sheet ST":
					company_education_allowance_chargeable_account_ = frappe.db.get_value("Company",company,"custom_education_allowance_chargeable_account_")
					if self.payment_type == _("Direct Payment"):
						create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.transaction_date)
						create_payment_journal_entry_from_payment_procedure(self,company_education_allowance_chargeable_account_,company_default_central_bank_account,self.total_amount,je_date=today())
					elif self.payment_type == _("Indirect Payment"):
						if self.middle_bank_account:
							create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.bank_enhancement_date)
							create_payment_journal_entry_from_payment_procedure(self,company_education_allowance_chargeable_account_,self.middle_bank_account,self.total_amount,je_date=today())
				
				elif self.reference_name == "Purchase Invoice":
					default_debit_account = frappe.db.get_value("Company",company,"default_payable_account")
					default_credit_account = frappe.db.get_value("Company",company,"custom_default_central_bank_account")
					create_journal_entry_from_payment_procedure_for_pi(self,default_debit_account,default_credit_account,self.total_amount,je_date=self.transaction_date,party_type=self.party_type,party_name=self.party_name_supplier)

			elif self.type == _("Unclassified"):
				create_payment_journal_entry_from_payment_procedure(self,company_default_payment_order_account,company_default_debit_account_mof,self.total_amount,je_date)
				if self.payment_type == _("Direct Payment"):
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.transaction_date)
					create_payment_journal_entry_from_payment_procedure(self,self.default_chargeable_account,company_default_central_bank_account,self.total_amount,je_date=today())
				elif self.payment_type == _("Indirect Payment"):
					if self.middle_bank_account:
						create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.bank_enhancement_date)
						create_payment_journal_entry_from_payment_procedure(self,self.default_chargeable_account,self.middle_bank_account,self.total_amount,je_date=today())

def create_journal_entry_from_payment_procedure_for_pi(doc,debit_account,credit_account,amount,je_date=None,party_type=None,party_name=None):
	if je_date == None:
		je_date = today()

	payment_je_doc = frappe.new_doc("Journal Entry")
	payment_je_doc.voucher_type = "Journal Entry"
	payment_je_doc.posting_date = je_date
	payment_je_doc.custom_payment_procedure_reference = doc.name

	accounts = []

	company = erpnext.get_default_company()
	company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")

	accounts_row = {
		"account":debit_account,
		"cost_center":company_default_cost_center,
		"debit_in_account_currency":amount,
	}

	account_type = frappe.get_cached_value("Account",debit_account, "account_type")
	if account_type in ["Receivable", "Payable"]:
		accounts_row["party_type"]=party_type
		accounts_row["party"]=party_name
		accounts_row["reference_type"]=doc.reference_name
		accounts_row["reference_name"]=doc.reference_no

	accounts.append(accounts_row)
	accounts_row_2 = {
		"account":credit_account,
		"cost_center":company_default_cost_center,
		"credit_in_account_currency":amount,
	}
	account_type = frappe.get_cached_value("Account",credit_account, "account_type")
	if account_type in ["Receivable", "Payable"]:
		accounts_row_2["party_type"]=party_type
		accounts_row_2["party"]=party_name
		accounts_row_2["reference_type"]=doc.reference_name
		accounts_row_2["reference_name"]=doc.reference_no
	accounts.append(accounts_row_2)

	payment_je_doc.set("accounts",accounts)
	payment_je_doc.run_method('set_missing_values')
	payment_je_doc.save(ignore_permissions=True)
	payment_je_doc.submit()

	frappe.msgprint(_("Payment Journal Entry is created from Payment Procedure {0}").format(get_link_to_form("Journal Entry",payment_je_doc.name)),alert=1)