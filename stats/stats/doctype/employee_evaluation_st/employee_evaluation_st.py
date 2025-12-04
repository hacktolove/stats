# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import get_link_to_form,add_to_date
from stats.api import calculate_actual_degree_based_on_weight


class EmployeeEvaluationST(Document):

	def validate(self):
		calculate_actual_degree_based_on_weight(self.employee_personal_goals)
		calculate_actual_degree_based_on_weight(self.employee_job_goals)
		calculate_actual_degree_based_on_weight(self.basic_competencies)
		calculate_actual_degree_based_on_weight(self.technical_competencies)
		calculate_actual_degree_based_on_weight(self.leadership)
		self.calculate_evaluation_summary()

	def on_update(self):
		if self.workflow_state:
			exists_in_bulk_evaluation = frappe.db.get_all("Bulk Evaluation Details ST",
												 parent_doctype = "Bulk Employee Evaluation ST",
												 filters={"evaluation_reference":self.name},
												 fields=["name","parent"])
			if len(exists_in_bulk_evaluation)>0:
				frappe.db.set_value("Bulk Evaluation Details ST",exists_in_bulk_evaluation[0].name,"workflow_status",self.workflow_state)
				
	def calculate_evaluation_summary(self):
		total_degree_of_personal_goals = 0
		total_degree_of_job_goals = 0
		total_degree_of_basic_competencies = 0
		total_degree_of_technical_competencies = 0
		total_degree_of_leadership = 0
		total_degree_of_competencies = 0

		if len(self.employee_personal_goals)>0:
			for row in self.employee_personal_goals:
				if row.actual_degree_based_on_weight:
					total_degree_of_personal_goals = total_degree_of_personal_goals + row.actual_degree_based_on_weight
		if len(self.employee_job_goals)>0:
			for goal in self.employee_job_goals:
				if goal.actual_degree_based_on_weight:
					total_degree_of_job_goals = total_degree_of_job_goals + goal.actual_degree_based_on_weight
		division_factor = 0
		if len(self.basic_competencies)>0:
			division_factor += 1
		if len(self.technical_competencies)>0:
			division_factor += 1
		if len(self.leadership)>0:
			division_factor += 1
		
		if len(self.basic_competencies)>0:
			for basic in self.basic_competencies:
				if basic.actual_degree_based_on_weight:
					total_degree_of_basic_competencies = total_degree_of_basic_competencies + basic.actual_degree_based_on_weight
		total_degree_of_basic_competencies = total_degree_of_basic_competencies

		if len(self.technical_competencies)>0:
			for technical in self.technical_competencies:
				if technical.actual_degree_based_on_weight:
					total_degree_of_technical_competencies = total_degree_of_technical_competencies + technical.actual_degree_based_on_weight
		total_degree_of_technical_competencies = total_degree_of_technical_competencies

		if len(self.leadership)>0:
			for leadership in self.leadership:
				if leadership.actual_degree_based_on_weight:
					total_degree_of_leadership = total_degree_of_leadership + leadership.actual_degree_based_on_weight
		total_degree_of_leadership = total_degree_of_leadership
		self.personal_goals = total_degree_of_personal_goals
		self.job_goals = total_degree_of_job_goals

		if division_factor>0:
			total_degree_of_competencies = (total_degree_of_basic_competencies + total_degree_of_technical_competencies + total_degree_of_leadership) / division_factor
		else :
			total_degree_of_competencies = 0

		self.competencies = total_degree_of_competencies
		
		stats_settings_doc = frappe.get_doc("Stats Settings ST")
		final_evaluation = 0

		if self.evaluation_type != "Test Period":
			personal_goal_weight, job_goal_weight, competencies_weight = frappe.db.get_value("Employee Grade",
																					self.grade,["custom_employee_personal_goal_weight",
																								"custom_employee_job_goal_weight",
																								"custom_competencies_weight"])
			if personal_goal_weight <= 0 or job_goal_weight <= 0 or competencies_weight <= 0:
				frappe.throw(_("Please set weights in Grade {0}".format(get_link_to_form("Employee Grade",self.grade))))
			else :
				final_evaluation = ((total_degree_of_personal_goals * personal_goal_weight / 100) + 
						(total_degree_of_job_goals * job_goal_weight / 100) + 
						(total_degree_of_competencies * competencies_weight / 100))
		
		elif self.evaluation_type == "Test Period":
			final_evaluation = (total_degree_of_competencies / 3)
			
		self.final_evaluation = final_evaluation
		if final_evaluation > 0:
			for row in stats_settings_doc.evaluation_slots:
				if final_evaluation >= row.lower_range and final_evaluation <= row.upper_range:
					self.evaluation_classification = row.evaluation_classification

	def on_submit(self):
		if self.action:
			if self.action == "Hire":
				frappe.db.set_value("Employee",self.employee_no,"custom_test_period_completed","Yes")
				frappe.msgprint(_("Test period is completed for employee {0}").format(self.employee_no),alert=1)

			employee_contract_doc = frappe.get_doc("Employee Contract ST",self.employee_contract_reference)
			if self.action == "Separate":
				frappe.db.set_value("Employee",self.employee_no,"status","Left")
				employee_contract_doc.status = "Separated"
				employee_contract_doc.save(ignore_permissions = True)
				frappe.msgprint(_("Employee Contract {0} status is changed to <b>{1}</b> ").format(get_link_to_form("Employee Contract ST",self.employee_contract_reference),"Separated"),alert=1)

			elif self.action == "Renew Test Period":
				employee_contract_doc.test_period_renewed = "Yes"
				employee_contract_doc.status = "Renewed"
				employee_contract_doc.end_of_new_test_period = add_to_date(employee_contract_doc.test_period_end_date, months=3)
				employee_contract_doc.save(ignore_permissions = True)
				frappe.msgprint(_("Employee Contract {0} is <b>{1}</b> ").format(get_link_to_form("Employee Contract ST",self.employee_contract_reference),"Renewed"),alert=1)
	
	@frappe.whitelist()
	def fetch_employee_different_goals(self):
		employee_personal_goal_details, employee_job_goal_details, basic_competencies, technical_competencies, leadership = None, None, None, None, None
		if self.employee_no:
			employee_personal_goal = frappe.db.get_all("Employee Personal Goals ST",
											  filters={"employee_no":self.employee_no,"docstatus":1},
											  fields=["name"])
			print(employee_personal_goal)
			if len(employee_personal_goal)>0:
				employee_personal_goal_doc = frappe.get_doc("Employee Personal Goals ST",employee_personal_goal[0].name)
				employee_personal_goal_details = employee_personal_goal_doc.personal_goals
				employee_job_goal_details = employee_personal_goal_doc.job_goals

		if self.designation:
			designation_doc = frappe.get_doc("Designation",self.designation)
			basic_competencies = designation_doc.custom_basic_competencies
			technical_competencies = designation_doc.custom_technical_competencies
			leadership = designation_doc.custom_leadership

			
		return employee_personal_goal_details, employee_job_goal_details, basic_competencies, technical_competencies, leadership
			
