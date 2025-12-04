# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_link_to_form
from frappe.model.document import Document


class BulkEmployeeEvaluationST(Document):
	
	@frappe.whitelist()
	def get_employees(self):
		if self.selection_type == "All Employee":
			all_active_employee_list = frappe.db.get_all("Employee",
												filters={"status":"Active"},
												fields=["name"])
		
		elif self.selection_type == "Filters":
			filters={"status":"Active"}

			if self.main_department:
				filters["department"]=self.main_department
			if self.sub_department:
				filters["custom_sub_department"]=self.sub_department
			if self.section:
				filters["custom_section"]=self.section

			all_active_employee_list = frappe.db.get_all("Employee",
												filters=filters,
												fields=["name"])
		 
		return all_active_employee_list

	@frappe.whitelist()
	def create_employee_evaluation(self):
		# today = getdate(nowdate())
		evaluation_list = []
		if len(self.bulk_evaluation_details)>0:
			for employee in self.bulk_evaluation_details:
				evaluation_dict = {}
				employee_doc = frappe.get_doc("Employee",employee.employee_no)
				employee_evaluation_doc = frappe.new_doc("Employee Evaluation ST")
				
				employee_evaluation_doc.employee_no = employee.employee_no
				employee_evaluation_doc.creation_date = self.creation_date
				employee_evaluation_doc.evaluation_type = self.evaluation_type
				employee_evaluation_doc.evaluation_from = self.from_date
				employee_evaluation_doc.evaluation_to = self.to_date
				
				employee_personal_goal = frappe.db.get_all("Employee Personal Goals ST",
												filters={"employee_no":employee.employee_no,"docstatus":1},
												fields=["name"])
				if len(employee_personal_goal)>0:
					employee_personal_goal_doc = frappe.get_doc("Employee Personal Goals ST",employee_personal_goal[0].name)
					if len(employee_personal_goal_doc.personal_goals)>0:
						for row in employee_personal_goal_doc.personal_goals:
							personal_goal = employee_evaluation_doc.append("employee_personal_goals",{})
							personal_goal.goals = row.goals
							personal_goal.weight = row.weight
							personal_goal.target_degree = row.target_degree

					if len(employee_personal_goal_doc.job_goals)>0:
						for row in employee_personal_goal_doc.job_goals:
							job_goal = employee_evaluation_doc.append("employee_job_goals",{})
							job_goal.goals = row.goals
							job_goal.weight = row.weight
							job_goal.uom = row.uom
							job_goal.target_degree = row.target_degree

				if employee_doc.designation:
					designation_doc = frappe.get_doc("Designation",employee_doc.designation)
					if len(designation_doc.custom_basic_competencies)>0:
						for row in designation_doc.custom_basic_competencies:
							basic_skill = employee_evaluation_doc.append("basic_competencies",{})
							basic_skill.competencies_name = row.competencies_name
							basic_skill.description = row.description
							basic_skill.weight = row.weight
							# basic_skill.degree_out_of_5 = row.degree_out_of_5
					
					if len(designation_doc.custom_technical_competencies)>0:
						for row in designation_doc.custom_technical_competencies:
							technical_skill = employee_evaluation_doc.append("technical_competencies",{})
							technical_skill.competencies_name = row.competencies_name
							technical_skill.description = row.description
							technical_skill.weight = row.weight
							# technical_skill.degree_out_of_5 = row.degree_out_of_5

					if len(designation_doc.custom_leadership)>0:
						for row in designation_doc.custom_leadership:
							leadership_skill = employee_evaluation_doc.append("leadership",{})
							leadership_skill.competencies_name = row.competencies_name
							leadership_skill.description = row.description
							leadership_skill.weight = row.weight
							# leadership_skill.degree_out_of_5 = row.degree_out_of_5

				employee_evaluation_doc.save(ignore_permissions=True)
				employee_evaluation_doc.add_comment("Comment",text="Created due to Bulk Employee Evaluation {0}".format(get_link_to_form("Bulk Employee Evaluation ST",self.name)))
				evaluation_dict["employee_no"] = employee.employee_no
				evaluation_dict["evaluation_reference"] = employee_evaluation_doc.name
				check_exists_active_workflow = frappe.db.exists("Workflow",{"is_active":1,"document_type":"Employee Evaluation ST"})
				if check_exists_active_workflow:
					evaluation_dict["evaluation_workflow_state"] = employee_evaluation_doc.workflow_state
				evaluation_list.append(evaluation_dict)
		
		return evaluation_list