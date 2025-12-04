# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EmployeeActingST(Document):

	def validate(self):
		self.validate_from_date_and_to_date()

	def on_submit(self):
		self.validate_status()

	def validate_from_date_and_to_date(self):
		if self.acting_from and self.acting_to:
			if self.acting_to < self.acting_from:
				frappe.throw(_("Acting To can not be less than Acting From"))

	def validate_status(self):
		if self.request_status:
			if self.request_status == None or self.request_status == "Pending":
				frappe.throw(_("Please Approve or Reject before submit"))