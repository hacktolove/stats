# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EvaluationClassificationST(Document):
	def validate(self):
		self.evaluation_classification_type()
		
	def evaluation_classification_type(self):
		if ((self.meet_expectation == 1 and (self.exceed_expectation == 1 or self.highly_exceed_expectation == 1)) or 
		(self.highly_exceed_expectation == 1 and (self.meet_expectation == 1 or self.exceed_expectation == 1)) or 
		(self.exceed_expectation == 1 and (self.highly_exceed_expectation == 1 or self.meet_expectation))):
			frappe.throw(_("You cannot Check Multiple Evaluation Classification Type"))
		
		if frappe.db.exists("Evaluation Classification ST", {"meet_expectation": 1, "name":["!=", self.name]}) and self.meet_expectation == 1:
			frappe.throw(_("Meet Expectation Evaluation Classification Type is Already Exist."))
		elif frappe.db.exists("Evaluation Classification ST", {"exceed_expectation": 1, "name":["!=", self.name]}) and self.exceed_expectation == 1:
			frappe.throw(_("Exceed Expectation Evaluation Classification Type is Already Exist."))
		elif frappe.db.exists("Evaluation Classification ST", {"highly_exceed_expectation": 1, "name":["!=", self.name]}) and self.highly_exceed_expectation == 1:
			frappe.throw(_("Highly Exceed Expectation Evaluation Classification Type is Already Exist."))
		else:
			pass
