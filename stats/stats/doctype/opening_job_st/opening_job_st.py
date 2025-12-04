# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class OpeningJobST(Document):
	pass

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_job_no(doctype, txt, searchfield, start, page_len, filters):
		
		job_list = frappe.get_all("MP Jobs Details ST", parent_doctype="Man Power Planning ST",filters={"hiring_plan_date": ["<=", nowdate()]}, 
							fields=["distinct job_no"], as_list=1)
		unique = tuple(set(job_list))
		# print(unique, '----------job_list-------------')
		return unique

@frappe.whitelist()
def get_job_deatils(job_title):
	job_deatils = frappe.db.get_value('MP Jobs Details ST', job_title, 
								   ['designation', 'main_job_department', 'sub_department', 'grade', 'section', 'branch', 'employment_type', 'contract_type', 'employee_unit'], as_dict=1)
	return job_deatils