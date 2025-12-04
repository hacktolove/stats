# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeInquiryST(Document):
	@frappe.whitelist()
	def get_employees_details_from_inquiry_type(self):
		inquiry_type = self.inquiry_type
		assigned_employee_details = frappe.db.sql("""
			SELECT itd.employee, itd.employee_name, e.company_email as email_id, e.cell_number as mobile_no
			FROM `tabInquiry Type Details ST` itd INNER JOIN `tabEmployee` e ON itd.employee = e.name
			WHERE itd.parent = '{0}'
		""".format(inquiry_type), as_dict=True)
		return assigned_employee_details
