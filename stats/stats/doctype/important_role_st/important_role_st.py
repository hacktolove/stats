# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ImportantRoleST(Document):
	def validate(self):
		self.calculate_importance_grade()

	def calculate_importance_grade(self):
		job_volume = frappe.db.get_single_value("Stats Settings ST","job_volume")
		scarcity_of_talent = frappe.db.get_single_value("Stats Settings ST", "scarcity_of_talent")
		strategic_impact = frappe.db.get_single_value("Stats Settings ST", "strategic_impact")
		if job_volume and scarcity_of_talent and strategic_impact:
			# Calculate the importance grade based on the formula
			if len(self.roles_details)>0:
				for row in self.roles_details:
					importance_grade_value, job_volume_value, scarcity_of_talent_value, strategic_impact_value = 0, 0, 0, 0
					if row.job_volume:
						job_volume_value = (row.job_volume / 100) * job_volume
					if row.scarcity_of_talent:
						scarcity_of_talent_value= (row.scarcity_of_talent / 100) * scarcity_of_talent
					if row.strategic_impact:
						strategic_impact_value = (row.strategic_impact / 100) * strategic_impact

					importance_grade_value = job_volume_value + scarcity_of_talent_value + strategic_impact_value
					row.importance_grade = importance_grade_value
		else:
			frappe.throw("Please set Job Volume ( % ), Scarcity of Talent ( % ) and Strategic Impact ( % ) in Stats Settings ST to calculate importance grade.")
