# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CertificateofAppreciationST(Document):
	pass

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_main_department_manager(doctype, txt, searchfield, start, page_len, filters):
	department_list = frappe.get_all("Department", filters={"is_group":1, "custom_main_department_manager":['!=', '']}, 
								  fields=["custom_main_department_manager"], as_list=1)
	unique = tuple(set(department_list))
	return unique