# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form, cint, date_diff, add_to_date, getdate
from erpnext.manufacturing.doctype.workstation.workstation import get_default_holiday_list


class PersonalTrainingRequestST(Document):
	def validate(self):
		no_of_days_for_personal_training = frappe.db.get_single_value("Stats Settings ST", "no_of_days_for_personal_training")
		difference_in_days = date_diff(self.training_start_date, self.date)+1
		allowed_date = add_to_date(self.date, days=no_of_days_for_personal_training)
		if no_of_days_for_personal_training :
			if difference_in_days < cint(no_of_days_for_personal_training):
				frappe.throw(_("You can apply for Personal Training after {0}".format(allowed_date)))
		else:
			frappe.throw(_("Please set No of days for Personal Training in {0}").format(get_link_to_form("Stats Settings ST", "Stats Settings ST")))

		if self.training_start_date and self.training_end_date:
			if getdate(self.training_start_date) > getdate(self.training_end_date):
				frappe.throw(_("Training Start Date cannot be after Training End Date."))

	def on_submit(self):
		self.create_training_evaluation()

	def on_update_after_submit(self):
		self.create_training_evaluation()


	@frappe.whitelist()
	def check_holiday_between_start_end_date(self):
		print("---------------------")
		default_holiday_list = get_default_holiday_list()
		print(default_holiday_list,"default_holiday_list")
		if default_holiday_list:
			holidays = frappe.db.get_all("Holiday",
								parent_doctype="Holiday List",
								filters={"parent":default_holiday_list,"holiday_date":["between",[self.training_start_date,self.training_end_date]]},
								fields=["name"])
			if len(holidays)>0:
				holiday_count = len(holidays)
				return holiday_count

	def create_training_evaluation(self):
		if self.acceptance_status == "Finished":
			training_evaluation_doc = frappe.new_doc("Training Evaluation ST")
			training_evaluation_doc.employee_no = self.employee_no
			training_evaluation_doc.personal_training_event = self.training_event
			training_evaluation_doc.training_classification = self.training_classification
			training_evaluation_doc.training_start_date = self.training_start_date
			training_evaluation_doc.training_end_date = self.training_end_date
			training_evaluation_doc.no_of_days = self.no_of_days
			training_evaluation_doc.total_of_hours = self.total_of_hours
			training_evaluation_doc.training_level = self.training_level
			training_evaluation_doc.training_method = self.training_method
			training_evaluation_doc.period = self.period
			training_evaluation_doc.city = self.city
			training_evaluation_doc.location = self.location
			training_evaluation_doc.required_certificate = self.required_certificate
			training_evaluation_doc.personal_training_request_reference = self.name
			# training_evaluation_doc.run_method("set_missing_values")
			training_evaluation_doc.save(ignore_permissions=True)
			frappe.msgprint(_("Training Evaluation is created {0}").format(get_link_to_form("Training Evaluation ST",training_evaluation_doc.name)),alert=True)
			return training_evaluation_doc.name