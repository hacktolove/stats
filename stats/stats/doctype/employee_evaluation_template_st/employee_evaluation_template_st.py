# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from stats.api import set_degree_based_on_weight,validate_weight


class EmployeeEvaluationTemplateST(Document):

	def validate(self):
		set_degree_based_on_weight(self.job_goals)
		validate_weight(self.job_goals)