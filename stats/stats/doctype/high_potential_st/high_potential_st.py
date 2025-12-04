# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import month_diff,today


class HighPotentialST(Document):
	pass
	@frappe.whitelist()
	def fetch_employees_from_employee_evaluation(self):
		filters = ""
		if self.main_department:
			filters += "and e.department = '{0}'".format(self.main_department)
		if self.sub_department:
			filters += "and e.custom_sub_department = '{0}'".format(self.sub_department)
		if self.section:
			filters += "and e.custom_section = '{0}'".format(self.section)

		employee_data = frappe.db.sql("""
					SELECT
						e.name as employee_no,
						e.employee_name ,
						e.department main_department ,
						e.custom_sub_department sub_department ,
						e.custom_section section,
						e.date_of_retirement,
						ee.name as employee_evaluation,
						ee.final_evaluation employee_evaluation_score,
						ee.evaluation_type
					FROM `tabEmployee` e
					LEFT OUTER JOIN (
					SELECT * FROM `tabEmployee Evaluation ST` WHERE evaluation_type ='Yearly' and docstatus =1) ee ON e.name=ee.employee_no 
					WHERE e.status ='Active' {0}
				""".format(filters), as_dict=1)
		print(employee_data, "employee_data===============")
		final_employee_list = []

		if len(employee_data)>0:
			for employee in employee_data:
				if self.no_of_years_for_retirement > 0.0:
					if employee.date_of_retirement:
						employee_years_of_retirement = month_diff(employee.date_of_retirement, today())/12
						print(employee_years_of_retirement,"employee_years_of_retirement",type(employee_years_of_retirement))
						if employee_years_of_retirement > self.no_of_years_for_retirement:
							final_employee_list.append(employee)
				else:
					final_employee_list.append(employee)
		print(final_employee_list,"final_employee_list===============")
		return final_employee_list
# @frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
# def get_employee_list(doctype, txt, searchfield, start, page_len, filters):
# 	no_of_years_for_retirement = filters.get("no_of_years_for_retirement")
# 	# searchfields = frappe.get_meta(doctype).get_search_fields()
# 	# searchfields = " or ".join(field + " like %(txt)s" for field in searchfields)
# 	if no_of_years_for_retirement:
# 		employee_list = frappe.db.sql("""
# 			SELECT name, employee_name,company_email, custom_idresidency_number, date_of_retirement FROM `tabEmployee`
# 			WHERE status = 'Active'
# 		""", as_dict=1)
# 		final_employee_list = []
# 		if len(employee_list) > 0:
# 			for employee in employee_list:
# 				if employee.date_of_retirement:
# 					employee_years_of_retirement = month_diff(employee.date_of_retirement, today()) / 12
# 					if employee_years_of_retirement > no_of_years_for_retirement:
# 						employee_name = (employee)
# 						final_employee_list.append(employee.name)
# 		print(final_employee_list, "final_employee_list after retirement filter")
# 		# if txt:
# 		# 	employee_list = []
# 		# 	for d in final_employee_list:
# 		# 		# if d[0].find(txt) != -1 or d[1].find(txt) != -1:
# 		# 		# 	employee_list.append(d)
# 		# 		if d.find(txt) != -1:
# 		# 			employee_list.append(d)
# 		# 	final_employee_list = employee_list 

# 		final_employee_tuple = tuple((i,) for i in final_employee_list)
# 		return final_employee_tuple