# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EmployeeTaskCompletionST(Document):
	def validate(self):
		# self.validate_approved_days()
		pass
	
	def validate_approved_days(self):
		if self.no_of_days and self.approved_days:
			if self.approved_days > self.no_of_days:
				frappe.throw(_("Approved days cannot be greater than no of days"))

	@frappe.whitelist()
	def fetch_trip_cost_details_from_template(self):
		template_details = []
		if self.trip_cost_template:
			trip_cost_template_doc = frappe.get_doc("Trip Cost Template ST", self.trip_cost_template)
			if len(trip_cost_template_doc.trip_cost_template_details)>0:
				for trip_cost in trip_cost_template_doc.trip_cost_template_details:
					details = {}
					details["element"] = trip_cost.element
					details["payment_method"] = trip_cost.payment_method
					template_details.append(details)
		return template_details
	
	# def on_submit(self):
	# 	if not self.approved_days:
	# 		frappe.throw(_("Please set approve days"))