# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, date_diff, cint, cstr
from stats.hr_utils import set_date_in_hijri

class EmployeeRetirementRequestST(Document):
	def validate(self):
		self.validate_retirement_date()
		self.validate_and_set_retirement_type()
		self.retirement_date_hijri = set_date_in_hijri(self.retirement_date_gregorian)

	def validate_and_set_retirement_type(self):
		age_diff_in_days = date_diff(self.retirement_date_gregorian, self.birth_date_gregorian)
		age_diff_in_years = age_diff_in_days / 360

		normal_years_of_retirement = frappe.db.get_value("Contract Type ST", self.contract_type, "normal_years_of_retirement")
		if normal_years_of_retirement and age_diff_in_years >= normal_years_of_retirement:
			self.retirement_type = "Normal Retirement"
		else:
			self.retirement_type = "Early Retirement"

		work_duration_in_days = date_diff(self.retirement_date_gregorian, self.employee_joining_date)
		working_years_based_on_hijri = work_duration_in_days / 354
		remaining_days = work_duration_in_days % 354

		self.total_working_years = working_years_based_on_hijri
		self.remaining_days = remaining_days

		if cint(working_years_based_on_hijri) < 25:
			frappe.throw(_("You cannot apply for retirement before completing 25 years (based on Hijri Calender) of service. Your completed years of service are {0}.").format(cint(working_years_based_on_hijri)))

	def validate_retirement_date(self):
		if getdate(self.birth_date_gregorian) >= getdate(self.retirement_date_gregorian):
			frappe.throw(_("Employee's Retirement Date Cannot be before Birth Date."))

	@frappe.whitelist()
	def create_retirement_request(self):
		rr = frappe.new_doc("Retirement Request ST")
		rr.employee_retirement_request = self.name
		rr.employee_no = self.employee_no
		rr.retirement_date_gregorian = self.retirement_date_gregorian

		rr.save(ignore_permissions=True)

		return rr.name
