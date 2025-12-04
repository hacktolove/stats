# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.utils import today, get_link_to_form
from frappe import _
from frappe.model.document import Document


class AchievementCertificateST(Document):
	
	def on_submit(self):
		self.create_payment_request_from_achievement_certificate()
		self.change_status_of_isp_request()

	def create_payment_request_from_achievement_certificate(self):
		company = erpnext.get_default_company()
		company_default_international_subscription_expense_account = frappe.db.get_value("Company",company,"custom_default_international_subscription_expense_account")
		
		pr_doc = frappe.new_doc("Payment Request ST")
		pr_doc.date = today()
		pr_doc.reference_name = "Achievement Certificate ST"
		pr_doc.reference_no = self.name
		pr_doc.type = "Classified"
		# else:
		# 	pr_doc.reference_name = self.reference_type
		# 	pr_doc.reference_no = self.invoice_reference
		pr_doc.budget_account = company_default_international_subscription_expense_account
		pr_doc.party_type = "Supplier"
		pr_doc.party_name_supplier = self.supplier
		pr_doc.total_amount = self.final_amount
		
		pr_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Request {0} is created").format(get_link_to_form("Payment Request ST", pr_doc.name)),alert=1)

	def change_status_of_isp_request(self):
		if self.reference_type != "International Subscription Payment Request ST":
			return
		isp_doc = frappe.get_doc("International Subscription Payment Request ST",self.invoice_reference)
		isp_doc.certificate_status = "Done"
		isp_doc.add_comment("Comment",text="Certificate changed to Done due to {0}".format(get_link_to_form("Achievement Certificate ST",self.name)))
		isp_doc.save(ignore_permissions=True)
		frappe.msgprint(_("International Subscription Payment Request certificate status changed to <b>Done</b>"),alert=True)
	
	@frappe.whitelist()
	def calculate_tax_on_invoice_amount(self):
		default_tax_template = frappe.db.get_all("Purchase Taxes and Charges Template",
										   filters={"is_default":1,"disabled":0},
										   fields = ['name'],limit=1)
		
		if len(default_tax_template) > 0:
			tax_rate = frappe.db.get_value("Purchase Taxes and Charges",
								  {"parent":default_tax_template[0].name},"rate")
			if tax_rate:
				print(self.invoice_amount,"invoice_amount")
				tax_amount = ( tax_rate * self.invoice_amount ) / 100
				print(tax_amount,"tax")
				return tax_amount
		
		else :
			frappe.throw(_("There is no Default Purchase Taxes and Charges Template"))
		