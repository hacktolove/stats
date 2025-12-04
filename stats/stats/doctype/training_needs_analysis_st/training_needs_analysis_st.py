# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document


class TrainingNeedsAnalysisST(Document):

	def validate(self):
		self.validate_start_date_and_end_date()

	def validate_start_date_and_end_date(self):
		if self.request_from_date and self.request_to_date:
			if self.request_to_date < self.request_from_date:
				frappe.throw(_("End date can not be less than Start date"))

	def on_submit(self):
		if len(self.training_needs_analysis_employee_details)>0:
			for row in self.training_needs_analysis_employee_details:
				if row.action == "Pending":
					frappe.throw(_("You cannot submit.<br>Please Approve or Reject Training Request {0} in row {1}").format(row.training_request_reference,row.idx))
		self.change_training_request_status()

	def change_training_request_status(self):
		if len(self.training_needs_analysis_employee_details)>0:
			for row in self.training_needs_analysis_employee_details:
				# frappe.db.set_value("Training Request ST",row.training_request_reference,"status",row.action)
				tr_doc = frappe.get_doc("Training Request ST",row.training_request_reference)
				tr_doc.status = row.action
				tr_doc.save(ignore_permissions=True)
				frappe.msgprint(_("Status of {0} is changed to {1}").format(get_link_to_form("Training Request ST", row.training_request_reference),row.action),alert=1)

	@frappe.whitelist()
	def fetch_training_request(self):
		if not self.request_from_date:
			frappe.throw(_("Request From Date is required"))
		if not self.request_to_date:
			frappe.throw(_("Request To Date is required"))

		from_date = frappe.utils.getdate(self.request_from_date)
		to_date = frappe.utils.getdate(self.request_to_date)

		filters={"docstatus":1,"status":"Pending","date":["between",[from_date,to_date]]}
		if self.main_department:
			filters["main_department"]=self.main_department
		if self.sub_department:
			filters["sub_department"]=self.sub_department
		if self.training_event:
			filters["training_event"]=self.training_event
		training_request_list = frappe.db.get_all("Training Request ST",
							  filters=filters,
							  fields=["name"])
		print(training_request_list,"training_request_list")
		final_training_request_list = []
		training_needs_analysis_list = frappe.db.get_all("Training Needs Analysis Employee Details ST",filters={"docstatus":0},fields=["training_request_reference"])

		for training_request in training_request_list:
			found=False
			if len(training_needs_analysis_list)>0:
				for training_analysis in training_needs_analysis_list:
					if training_analysis.training_request_reference == training_request.name:
						found=True
						break
			if found==False:
				final_training_request_list.append(training_request)
							
		return final_training_request_list
		# return training_request_list