# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class ResignationTypeST(Document):
	def validate(self):
		self.validate_resignation_type()

	def validate_resignation_type(self):
		if ((self.is_it_separation == 1 and (self.is_it_not_renewal_of_contract == 1 or self.is_it_resignation == 1 or self.is_it_test_period_resignation == 1)) or 
			(self.is_it_resignation == 1 and (self.is_it_separation == 1 or self.is_it_not_renewal_of_contract == 1 or self.is_it_test_period_resignation == 1)) or 
			(self.is_it_not_renewal_of_contract == 1 and (self.is_it_resignation == 1 or self.is_it_separation or self.is_it_test_period_resignation == 1)) or
			(self.is_it_test_period_resignation == 1 and (self.is_it_resignation == 1 or self.is_it_separation or self.is_it_not_renewal_of_contract == 1))):
			frappe.throw(_("You cannot Check Multiple Resignation Type"))

		if frappe.db.exists("Resignation Type ST", {"is_it_separation": 1, "name":["!=", self.name]}) and self.is_it_separation == 1:
			frappe.throw(_("Separation Resignation Type is Already Exist."))
		elif frappe.db.exists("Resignation Type ST", {"is_it_not_renewal_of_contract": 1, "name":["!=", self.name]}) and self.is_it_not_renewal_of_contract == 1:
			frappe.throw(_("It is not Renewal of contract Resignation Type is Already Exist."))
		elif frappe.db.exists("Resignation Type ST", {"is_it_resignation": 1, "name":["!=", self.name]}) and self.is_it_resignation == 1:
			frappe.throw(_("It is Resignation Type is Already Exist."))
		elif frappe.db.exists("Resignation Type ST", {"is_it_test_period_resignation": 1, "name":["!=", self.name]}) and self.is_it_test_period_resignation == 1:
			frappe.throw(_("It is Resignation Type is Already Exist."))
		else:
			pass