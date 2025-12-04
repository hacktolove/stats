# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ScholarshipST(Document):
	def validate(self):
		self.validate_scholarship_start_and_end_date()

	def validate_scholarship_start_and_end_date(self):
		if self.apply_end_date:
			for row in self.scholarship_details:
				if row.scholarship_start_date:
					if row.scholarship_start_date < self.apply_end_date:
						frappe.throw(_("Row #{0} Scholarship start date cannot be greater than apply end date").format(row.idx))