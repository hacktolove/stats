# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, add_to_date
from erpnext.setup.doctype.employee.employee import is_holiday
from frappe.model.document import Document


class EmployeeBreastFeedingRequestST(Document):
	def validate(self):
		self.validate_dates()
		self.calculate_total_no_of_days()
	
	def validate_dates(self):
		if self.from_date and self.to_date:
			if self.from_date > self.to_date:
				frappe.throw(_("From Date should be less than To Date"))
	
	def calculate_total_no_of_days(self):
		total_no_of_working_days = 0
		if self.from_date and self.to_date:
			total_no_of_days = date_diff(self.to_date, self.from_date) + 1
			for day in range(total_no_of_days):
				new_date = add_to_date(self.from_date, days=day)
				holiday = is_holiday(self.employee_no, new_date)
				if holiday == False:
					total_no_of_working_days = total_no_of_working_days + 1
			self.total_no_of_days = total_no_of_working_days
		else:
			self.total_no_of_days = total_no_of_working_days
