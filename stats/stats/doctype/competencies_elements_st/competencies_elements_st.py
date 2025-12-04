# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document


class CompetenciesElementsST(Document):
	
	@frappe.whitelist()
	def set_default_levels(self):
		stats_settings_doc = frappe.get_doc("Stats Settings ST","Stats Settings ST")
		if not (stats_settings_doc.level_1 or stats_settings_doc.level_2 or stats_settings_doc.level_3):
			frappe.throw(_("Please set default levels in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))