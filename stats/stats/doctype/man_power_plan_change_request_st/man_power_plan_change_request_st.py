# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class ManPowerPlanChangeRequestST(Document):
	def validate(self):
		self.validate_job_no()
		# self.set_finance_imapct()

	def on_submit(self):
		self.change_pervious_job_details()
		self.create_new_job_details()

	def validate_job_no(self):
		if self.request_type == "New Job":
			if frappe.db.exists('MP Jobs Details ST', self.new_job_no):
				frappe.throw(_("{0} Job No details are already exist, Please create new jon no.").format(self.new_job_no))
				return
			
	def set_finance_imapct(self):
		if not self.is_new():
			man_power = frappe.get_doc("Man Power Planning ST", self.man_power_planning_reference)
			self.original_budget_amount = man_power.planned_budget

			if self.request_type == "Update Existing Job":
				old_salary = self.salary * 12
				new_salary = self.salary_cp * 12
				self.new_budgeted_amount = self.original_budget_amount - old_salary + new_salary

			if self.request_type == "New Job":
				self.new_budgeted_amount = self.original_budget_amount + self.salary_nj * 12

			self.finance_impact = self.original_budget_amount - self.new_budgeted_amount


	def change_pervious_job_details(self):
		if self.request_type == "Update Existing Job":
			frappe.db.set_value('MP Jobs Details ST',self.job_no, 'designation', self.designation_cp)
			frappe.db.set_value('MP Jobs Details ST',self.job_no, 'main_job_department', self.main_department_cp)
			frappe.db.set_value('MP Jobs Details ST',self.job_no, 'sub_job_department', self.sub_department_cp)
			frappe.db.set_value('MP Jobs Details ST',self.job_no, 'grade', self.grade_cp)
			# frappe.db.set_value('MP Jobs Details ST',self.job_no, 'salary', self.salary_cp)
			frappe.db.set_value('MP Jobs Details ST',self.job_no, 'section', self.section_cp)
			frappe.db.set_value('MP Jobs Details ST',self.job_no, 'employee_unit', self.employee_unit_cp)

			frappe.msgprint(_("Update Job No. {0} Details in Man Power Planning {1}").format(self.job_no, self.man_power_planning_reference), alert=1)
			

	def create_new_job_details(self):
		if self.request_type == "New Job":
			new_job = frappe.new_doc("Job No ST")
			new_job.job_no = self.new_job_no
			new_job.save(ignore_permissions=True)

			man_power = frappe.get_doc('Man Power Planning ST', self.man_power_planning_reference)
			row = man_power.append("job_details")
			row.job_no = new_job.name
			row.designation = self.designation_nj
			row.main_job_department = self.main_department_nj
			row.sub_department = self.sub_department_nj
			row.grade = self.grade_np
			row.section = self.section_nj
			row.employee_unit = self.employee_unit_nj

			# row.salary = self.salary_nj

			man_power.save(ignore_permissions=True)

			frappe.msgprint(_("Add New Job No. {0} in Man Power Planning {1}").format(self.job_no, self.man_power_planning_reference), alert=1)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_job_no(doctype, txt, searchfield, start, page_len, filters):
		
		parent = filters.get('parent')
		job_details = frappe.get_all("MP Jobs Details ST", filters={"parent":parent}, fields=["name"], as_list=1)
		job_no = tuple(set(job_details))
		# print(unique, '----------ab')
		return job_no