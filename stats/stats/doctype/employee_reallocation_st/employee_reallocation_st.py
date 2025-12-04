# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form
from stats.api import get_base_amount_from_salary_structure_assignment


class EmployeeReallocationST(Document):
	def validate(self):
		# self.validate_new_branch()
		self.validate_new_sub_department()
		# self.validate_new_section()
		self.validate_due_amount()

	# logic for due_amount is pending

	def validate_new_branch(self):
		if self.new_branch:
			if self.new_branch == self.branch:
				frappe.throw(_("Branch and New branch must be different"))
		
	def validate_new_sub_department(self):
		if self.new_sub_department:
			if self.new_sub_department == self.sub_department:
				frappe.throw(_("Sub department and New sub department must be different"))

	def validate_new_section(self):
		if self.new_section:
			if self.new_section == self.section:
				frappe.throw(_("Section and New section must be different"))

	def validate_due_amount(self):
		amount_from_ssa = get_base_amount_from_salary_structure_assignment(self.employee_no)
		print(amount_from_ssa,"amount_from_ssa")
		if amount_from_ssa > 0:
			maximum_reallocation_amount = frappe.db.get_single_value("Stats Settings ST","maximum_reallocation_amount")
			if maximum_reallocation_amount:
				if amount_from_ssa > maximum_reallocation_amount:
					self.due_amount = maximum_reallocation_amount
					frappe.msgprint(_("Maximum reallocation amount is set in due amount"),alert=True)
				elif amount_from_ssa <= maximum_reallocation_amount:
					self.due_amount = amount_from_ssa
					frappe.msgprint(_("Due amount is set based on employee's salary structure assignment"),alert=True)
			else:
				frappe.throw(_("Please set maximum reallocation amount in stats settings"))
		else:
			frappe.throw(_("Due amount cannot be zero"))
				
	def on_submit(self):
		employee_doc = frappe.get_doc("Employee",self.employee_no)
		employee_doc.department = self.new_main_department
		employee_doc.custom_sub_department = self.new_sub_department
		employee_doc.branch = self.new_branch
		employee_doc.custom_section = self.new_section
		employee_doc.add_comment("Comment", text='Due to Employee Reallocation {0}<br>Main department changed {1} to {2}<br>Sub department changed {3} to {4}<br>Branch changed {5} to {6}<br>Section changed {7} to {8}'
						   .format(get_link_to_form("Employee Reallocation ST",self.name),frappe.bold(self.main_department),frappe.bold(self.new_main_department),frappe.bold(self.sub_department),frappe.bold(self.new_sub_department),frappe.bold(self.branch),frappe.bold(self.new_branch),frappe.bold(self.section),frappe.bold(self.new_section)))
		employee_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Employee details are changed"),alert=True)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_employee_based_on_main_department(doctype, txt, searchfield, start, page_len, filters):
	main_department = filters.get("main_department")
	employee_list = frappe.db.get_all("Employee",
				   filters={"department":main_department},
				   fields=["name","employee_name"],as_list=1)
	return employee_list