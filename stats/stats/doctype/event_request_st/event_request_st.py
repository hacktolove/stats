# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class EventRequestST(Document):
	def on_submit(self):
		self.validate_all_table_are_filled_or_not()

	def validate_all_table_are_filled_or_not(self):
		if len(self.gm_details) == 0:
			frappe.throw(_("Please select Employee in GM Details"))

		if len(self.department_manager_details) == 0: 
			frappe.throw(_("Please select Employee in Department Manager Details"))

		if len(self.candidate_details) == 0:
			frappe.throw(_("Please select Employee in Candidate Details"))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_ongoing_events_as_per_request_creation_date(doctype, txt, searchfield, start, page_len, filters):
	ongoing_events = []
	req_creation_date = frappe.utils.getdate(filters.get('creation_date'))
	events = frappe.db.sql("SELECT te.name FROM `tabEvent ST` te WHERE te.docstatus = 1;", as_list = 1)
	if len(events) > 0:
		for event in events:
			doc = frappe.get_doc("Event ST", event)
			event_creation_date = doc.creation_date
			event_valid_till = frappe.utils.add_to_date(event_creation_date, days=int(doc.validation)-1)
			(event, event_creation_date, event_valid_till)
			if req_creation_date >= event_creation_date and req_creation_date <= event_valid_till:
				ongoing_events.append(event)
		
		filtered_events = tuple(ongoing_events)
		return filtered_events

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def filter_employees_based_on_logged_in_user(doctype, txt, searchfield, start, page_len, filters):
	logged_in_user = frappe.db.get_value("Employee", {'company_email' : filters.get('reports_to')}, "name")
	if logged_in_user != None:
		employees = frappe.db.sql("SELECT e.name FROM `tabEmployee` e WHERE e.reports_to = '{0}' AND e.name LIKE %(txt)s;".format(logged_in_user), {"txt": "%%%s%%" % txt})
		return employees