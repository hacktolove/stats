# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document


class InternationalSubscriptionPaymentRequestST(Document):
	
	@frappe.whitelist()
	def create_achievement_certificate(self):
		certificate_doc = frappe.new_doc("Achievement Certificate ST")
		certificate_doc.reference_type = self.doctype
		certificate_doc.invoice_reference = self.name
		certificate_doc.description = self.description
		certificate_doc.supplier = self.supplier
		certificate_doc.project_owner = self.project_owner
		certificate_doc.payment_amount = self.subscription_amount
		certificate_doc.project_manager = self.project_manager
		certificate_doc.contract_date = self.contract_date
		certificate_doc.contract_period = self.contract_period
		certificate_doc.run_method("set_missing_values")
		certificate_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Achievement Certificate is created {0}".format(get_link_to_form("Achievement Certificate ST",certificate_doc.name))),alert=True)

		return certificate_doc.name