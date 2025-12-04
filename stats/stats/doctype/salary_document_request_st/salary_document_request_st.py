# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from stats.salary import get_latest_salary_structure_assignment
from frappe.model.document import Document


class SalaryDocumentRequestST(Document):
	@frappe.whitelist()
	def get_salary_details(self):
		salary_details = []
		latest_salary_structure_assignment = get_latest_salary_structure_assignment(self.employee_no,self.request_date)
		if latest_salary_structure_assignment:
			salary_structure = frappe.db.get_value("Salary Structure Assignment",latest_salary_structure_assignment,"salary_structure")
			if salary_structure:
				salary_structure_doc = frappe.get_doc("Salary Structure",salary_structure)
				for row in salary_structure_doc.earnings:
					salary_row = {}
					salary_row["salary_component"] = row.salary_component
					salary_row["amount"] = row.amount
					salary_details.append(salary_row)
		
		return salary_details
