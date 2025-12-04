# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import erpnext
from frappe.utils import cint, get_link_to_form, today
from frappe.model.document import Document
from stats.salary import get_latest_salary_structure_assignment

class EmployeeAnnualRewardST(Document):
	def validate(self):
		self.calcualte_reward_value()
	
	def on_submit(self):
		self.create_payment_request()

	def calcualte_reward_value(self):
		if len(self.employee_annual_reward_details) > 0:
			for reward in self.employee_annual_reward_details:
				salary_assignment = get_latest_salary_structure_assignment(reward.employee_no, self.creation_date)
				salary_structure = frappe.db.get_value("Salary Structure Assignment", salary_assignment, "salary_structure")
				ss = frappe.get_doc("Salary Structure", salary_structure)

				reward_amount = 0
				for ear in ss.earnings:
					include_in_reward = frappe.db.get_value("Salary Component", ear.salary_component, "custom_include_in_reward")
					if include_in_reward == 1:
						reward_amount = reward_amount + ear.amount

				evaluation_classification = frappe.get_doc("Evaluation Classification ST", reward.evaluation_classification)
				stats_settings_doc = frappe.get_doc("Stats Settings ST","Stats Settings ST")
				print(stats_settings_doc.salary_count_for_meet_expectation,'stats_settings_doc.stats_settings_doc.stats_settings_doc.')
				if stats_settings_doc.salary_count_for_meet_expectation in [None,0] or stats_settings_doc.salary_count_for_exceed_expectation in [None,0] or stats_settings_doc.salary_count_for_highly_exceed_expectation in [None,0]:
					frappe.throw(_("Please set Salary Count for Evaluation Classification in {0}").format(get_link_to_form("Stats Settings ST","Stats Settings ST")))
				if evaluation_classification.meet_expectation == 1:
					reward.reward_value = reward_amount * stats_settings_doc.salary_count_for_meet_expectation or 0
				elif evaluation_classification.exceed_expectation == 1:
					reward.reward_value = reward_amount * stats_settings_doc.salary_count_for_exceed_expectation or 0
				elif evaluation_classification.highly_exceed_expectation == 1:
					reward.reward_value = reward_amount * stats_settings_doc.salary_count_for_highly_exceed_expectation or 0
				else:
					frappe.msgprint(_("In {0} :Please Set Evaluation Classification Expectation Type.").format(get_link_to_form(evaluation_classification.doctype,evaluation_classification.name)))
	
	@frappe.whitelist()
	def fetch_employee_based_on_classification(self):
		employee_evaluation_list = frappe.db.get_all("Employee Evaluation ST",
											   filters={"evaluation_type":self.evaluation_type},
											   fields=["name","employee_no","evaluation_from","evaluation_classification","final_evaluation"])
		
		final_list = []
		if len(employee_evaluation_list)>0:
			for record in employee_evaluation_list:
				emp_details = {}
				if (record.evaluation_from).year == cint(self.reward_year):
					if record.evaluation_classification in [ele.evaluation_classification for ele in self.select_evaluation]:
						emp_details["employee_no"]=record.employee_no
						emp_details["evaluation_classification"]=record.evaluation_classification
						emp_details["final_evaluation"]=record.final_evaluation

						final_list.append(emp_details)
		print(final_list,'---------')
		return final_list
	
	def create_payment_request(self):
		company = erpnext.get_default_company()
		company_annual_reward_expense_account = frappe.db.get_value("Company",company,"custom_annual_reward_expense_account")
		pr_doc = frappe.new_doc("Payment Request ST")
		pr_doc.date = today()
		pr_doc.reference_name = self.doctype
		pr_doc.reference_no = self.name
		pr_doc.budget_account = company_annual_reward_expense_account
		pr_doc.party_type = "Employee"
		pr_doc.type = "Classified"
		
		if len(self.employee_annual_reward_details)>0:
			for row in self.employee_annual_reward_details:
				pr_row = pr_doc.append("employees",{})
				pr_row.employee_no = row.employee_no
				pr_row.amount = row.reward_value

		pr_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Request {0} is created").format(get_link_to_form("Payment Request ST", pr_doc.name)),alert=1)