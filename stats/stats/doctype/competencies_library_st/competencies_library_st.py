# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class CompetenciesLibraryST(Document):
	pass

@frappe.whitelist()
def set_elements_in_childtable(element):
	
	elements_list = json.loads(element)
	elements = ",".join(i.get("elements") for i in elements_list)
	
	return elements