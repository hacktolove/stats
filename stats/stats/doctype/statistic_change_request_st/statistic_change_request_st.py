# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_link_to_form
from frappe import _

class StatisticChangeRequestST(Document):
	def on_submit(self):
		self.set_new_values_in_statistic_request()

	def set_new_values_in_statistic_request(self):
		doc = frappe.get_doc("Statistic Request ST", self.statistic_request_reference)
		if self.new_number_of_researchers and self.new_number_of_researchers != 0:
			doc.no_of_researchers = self.new_number_of_researchers
		
		if self.new_number_of_inspectors and self.new_number_of_inspectors != 0:
			doc.no_of_inspectors = self.new_number_of_inspectors
		
		if self.new_no_of_support_team and self.new_no_of_support_team != 0:
			doc.no_of_support_team = self.new_no_of_support_team

		# if self.new_no_of_workers and self.new_no_of_workers != 0:
		# 	doc.no_of_workers = self.new_no_of_workers

		if self.new_no_of_supervisor and self.new_no_of_supervisor != 0:
			doc.no_of_supervisor = self.new_no_of_supervisor

		# if self.new_no_of_days and self.new_no_of_days != 0:	
		# 	doc.no_of_days = self.new_no_of_days

		if self.new_statistics_method and self.new_statistics_method != '':
			doc.statistics_method = self.new_statistics_method

		if self.new_planned_start_date:
			doc.planned_start_date = self.new_planned_start_date
		
		if self.new_planned_end_date:
			doc.planned_end_date = self.new_planned_end_date

		doc.add_comment("Comment",text="This Doc Updated Because Of Statistic Change Request {0} doc.".format(get_link_to_form("Statistic Change Request ST",self.name)))
		doc.save(ignore_permissions=True)
		frappe.msgprint(_("Fields are updated with new values"), alert=1)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_final_approved_statistic_request(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.get_all("Statistic Request ST", filters={"docstatus":1, "approval_status":"Final Approval"}, fields=["name"], as_list=1)