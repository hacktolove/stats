# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document


class PurchasingCommitteeST(Document):
	def on_submit(self):
		self.change_status_in_material_request()

	def change_status_in_material_request(self):
		if self.material_request_reference:
			material_request_doc = frappe.get_doc("Material Request",self.material_request_reference)
			material_request_doc.custom_purchasing_committee_status = "Finished"
			material_request_doc.add_comment("Comment",text="Purchasing Committee Status changed to <b>Finished</b> due to {0}".format(get_link_to_form(self.doctype,self.name)))
			material_request_doc.save(ignore_permissions = True)
			frappe.msgprint(_("Material Request {0} Purchasing Committee Status changed to <b>Finished</b>".format(get_link_to_form("Material Request",self.material_request_reference))),alert=True)