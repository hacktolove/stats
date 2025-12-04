# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate

class ManPowerPlanningST(Document):
	def validate(self):	
		print("=====validate====")
		self.create_job_no()
		self.set_job_no_in_employee()
		self.change_position_status_in_job_details()
		# self.set_budget_details()

	def create_job_no(self):
		if len(self.job_details) > 0:
			for job in self.job_details:
				if job.job_no == None or job.job_no == "":
					job_no = frappe.new_doc("Job No ST")
					job_no.save(ignore_permissions=True)
					job_no.job_no = job_no.name
					job_no.save(ignore_permissions=True)

					job.job_no = job_no.name
					job.name = job_no.name
				else:
					job.name = job.job_no
					

	def set_job_no_in_employee(self):
		if len(self.job_details) > 0:
			for job in self.job_details:
				if job.employee_no:
					employee = frappe.get_doc('Employee', job.employee_no)
					if employee.custom_job_no == None:
						employee.custom_job_no = job.job_no
						employee.save(ignore_permissions=True)
						frappe.msgprint(_("In Employee {0} Job No set to {1}").format(employee.name, job.job_no), alert=True)
				else:
					pass

	def change_position_status_in_job_details(self):
		if len(self.job_details):
			for job in self.job_details:
				if job.employee_no:
					job.position_status = "Filled"
				elif not job.employee_no and job.position_status == "Filled":
					job.position_status = "Vacant"
					job.supply_name = None

	def set_budget_details(self):
		self.year = getdate(self.from_date).year

		if not self.is_new() and len(self.job_details) > 0:

			############ planned_budget #########
			company = erpnext.get_default_company()
			salary_expense_account = frappe.db.get_value("Company", company, "custom_default_salary_expense_account")
			department_budget_list = frappe.db.get_list("Department Budget ST", filters={"fiscal_year":self.year, "main_department":self.main_department},
											   fields=["name"])
	
			planned_budget = 0
			if len(department_budget_list) > 0:
				for db in department_budget_list:
					db_doc = frappe.get_doc("Department Budget ST", db.name)
					for account in db_doc.account_table:
						if account.budget_expense_account == salary_expense_account:
							planned_budget = planned_budget + account.approved_amount
							break
			else:
				pass
				# frappe.throw(_("For {0} No Buget Found for {1} Main department").format(self.year, self.main_department))
			
			self.planned_budget = planned_budget

			########### consumed_budget ##########

			consumed_budget = 0
			for job in self.job_details:
				if job.position_status == "Filled":
					consumed_budget = consumed_budget + job.salary

			self.consumed_budget = consumed_budget * 12

			if self.planned_budget > 0:
				self.remaining_budget = self.planned_budget - self.consumed_budget


