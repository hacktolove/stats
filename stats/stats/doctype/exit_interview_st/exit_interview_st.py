# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form

class ExitInterviewST(Document):
	def validate(self):
		self.check_already_exists_exit_interview()
		if not self.is_new():
			self.check_atleast_one_leaving_reason_exists()
			self.not_allow_to_select_multiple_evaluation_option()
			self.check_if_questions_answer_given_or_not()
	
	def on_submit(self):
		if self.resignation_reference:
			resignation_doc = frappe.get_doc("Employee Resignation ST", self.resignation_reference)
			resignation_doc.exit_interview_status = "Processed"
			frappe.msgprint(_("In Employee Resignation: {0} Exit Interview Status Set to 'Processed'.").format(self.resignation_reference), alert=1)
			resignation_doc.add_comment("Comment",text="Exit Interview Status Set to <b>Processed</b> due to {0}".format(get_link_to_form(self.doctype,self.name)))
			resignation_doc.save(ignore_permissions=True)

	def on_trash(self):
		if self.resignation_reference:
			resignation_doc = frappe.get_doc("Employee Resignation ST", self.resignation_reference)
			resignation_doc.exit_interview_status = "Pending"
			frappe.msgprint(_("In Employee Resignation: {0} Exit Interview Status Set to 'Pending'.").format(self.resignation_reference), alert=1)
			resignation_doc.add_comment("Comment",text="Exit Interview Status Set to <b>Pending</b> due to delete {0} document".format(self.name))
			resignation_doc.save(ignore_permissions=True)

	def check_already_exists_exit_interview(self):
		if self.resignation_reference:
			exit_interview_exists = frappe.db.exists("Exit Interview ST",{"resignation_reference": self.resignation_reference, "name": ["!=", self.name]})
			if exit_interview_exists:
				frappe.throw(_("Employee Exit Interview for {0} Resignation Request is Already Done.").format(self.resignation_reference))
			
			resignation_status = frappe.db.get_value("Employee Resignation ST", self.resignation_reference, "docstatus")
			if resignation_status != 1:
				frappe.throw(_("Exit Interview can be created only for Submitted Employee Resignation."))

		elif self.retirement_reference:
			exit_interview_exists = frappe.db.exists("Exit Interview ST",{"retirement_reference": self.retirement_reference, "name": ["!=", self.name]})
			if exit_interview_exists:
				frappe.throw(_("Employee Exit Interview for {0} Retirement Request is Already Done.").format(self.retirement_reference))
			
			resignation_status = frappe.db.get_value("Retirement Request ST", self.retirement_reference, "docstatus")
			if resignation_status != 1:
				frappe.throw(_("Exit Interview can be created only for Submitted Employee Retirement."))

	def check_atleast_one_leaving_reason_exists(self):
		leaving_reason_exists = False
		if self.dissatisfaction_with_salary_and_benefits == 1:
			leaving_reason_exists = True
		elif self.poor_work_environment == 1:
			leaving_reason_exists = True
		elif self.better_job_offer == 1:
			leaving_reason_exists = True
		elif self.lack_of_job_security == 1:
			leaving_reason_exists = True
		elif self.lack_of_clarity == 1:
			leaving_reason_exists = True
		elif self.lack_of_development_and_promotion_opportunities == 1:
			leaving_reason_exists = True
		elif self.high_stress_and_poor_worklife_balance == 1:
			leaving_reason_exists = True
		elif self.lack_of_appreciation_and_recognition_of_efforts == 1:
			leaving_reason_exists = True
		elif self.differences_in_values_and_goals == 1:
			leaving_reason_exists = True
		elif self.lack_of_proper_supervision == 1:
			leaving_reason_exists = True


		if leaving_reason_exists == False :
			frappe.throw(_("Please select at least one <b>Leaving Reason</b>"))

	def not_allow_to_select_multiple_evaluation_option(self):

		select_work_environment_evaluation_option = []

		if self.work_environment_ex == 1:
			select_work_environment_evaluation_option.append(self.work_environment_ex)
		if self.work_environment_vg == 1:
			select_work_environment_evaluation_option.append(self.work_environment_vg)
		if self.work_environment_go == 1:
			select_work_environment_evaluation_option.append(self.work_environment_go)
		if self.work_environment_wk == 1:
			select_work_environment_evaluation_option.append(self.work_environment_wk)
		if self.work_environment_vwk == 1:
			select_work_environment_evaluation_option.append(self.work_environment_vwk)
		print(len(select_work_environment_evaluation_option),"+++++++",select_work_environment_evaluation_option)


		select_salary_evaluation_option = []

		if self.salary_ex == 1:
			select_salary_evaluation_option.append(self.salary_ex)
		elif self.salary_vg == 1:
			select_salary_evaluation_option.append(self.salary_vg)
		elif self.salary_go == 1:
			select_salary_evaluation_option.append(self.salary_go)
		elif self.salary_wk == 1:
			select_salary_evaluation_option.append(self.salary_wk)
		elif self.salary_vwk == 1:
			select_salary_evaluation_option.append(self.salary_vwk)
		print(len(select_salary_evaluation_option),"+++++++",select_salary_evaluation_option)

		select_treatment_evaluation_option = []

		if self.treatment_ex == 1:
			select_treatment_evaluation_option.append(self.treatment_ex)
		if self.treatment_vg == 1:
			select_treatment_evaluation_option.append(self.treatment_vg)
		if self.treatment_go == 1:
			select_treatment_evaluation_option.append(self.treatment_go)
		if self.treatment_wk == 1:
			select_treatment_evaluation_option.append(self.treatment_wk)
		if self.treatment_vwk == 1:
			select_treatment_evaluation_option.append(self.treatment_vwk)
		print(len(select_treatment_evaluation_option),"+++++++",select_treatment_evaluation_option)

		select_work_training_evaluation_option = []

		if self.work_training_ex == 1:
			select_work_training_evaluation_option.append(self.work_training_ex)
		if self.work_training_vg == 1:
			select_work_training_evaluation_option.append(self.work_training_vg)
		if self.work_training_go == 1:
			select_work_training_evaluation_option.append(self.work_training_go)
		if self.work_training_wk == 1:
			select_work_training_evaluation_option.append(self.work_training_wk)
		if self.work_training_vwk == 1:
			select_work_training_evaluation_option.append(self.work_training_vwk)
		print(len(select_work_training_evaluation_option),"+++++++",select_work_training_evaluation_option)

		select_team_work_evaluation_option = []

		if self.team_work_ex == 1:
			select_team_work_evaluation_option.append(self.team_work_ex)
		if self.team_work_vg == 1:
			select_team_work_evaluation_option.append(self.team_work_vg)
		if self.team_work_go == 1:
			select_team_work_evaluation_option.append(self.team_work_go)
		if self.team_work_wk == 1:
			select_team_work_evaluation_option.append(self.team_work_wk)
		if self.team_work_vwk == 1:
			select_team_work_evaluation_option.append(self.team_work_vwk)
		print(len(select_team_work_evaluation_option),"+++++++",select_team_work_evaluation_option)

		select_communication_evaluation_option = []

		if self.communication_ex == 1:
			select_communication_evaluation_option.append(self.communication_ex)
		if self.communication_vg == 1:
			select_communication_evaluation_option.append(self.communication_vg)
		if self.communication_go == 1:
			select_communication_evaluation_option.append(self.communication_go)
		if self.communication_wk == 1:
			select_communication_evaluation_option.append(self.communication_wk)
		if self.communication_vwk == 1:
			select_communication_evaluation_option.append(self.communication_vwk)
		print(len(select_communication_evaluation_option),"+++++++",select_communication_evaluation_option)

		select_supervising_evaluation_option = []

		if self.supervising_ex == 1:
			select_supervising_evaluation_option.append(self.supervising_ex)
		if self.supervising_vg == 1:
			select_supervising_evaluation_option.append(self.supervising_vg)
		if self.supervising_go == 1:
			select_supervising_evaluation_option.append(self.supervising_go)
		if self.supervising_wk == 1:
			select_supervising_evaluation_option.append(self.supervising_wk)
		if self.supervising_vwk == 1:
			select_supervising_evaluation_option.append(self.supervising_vwk)
		print(len(select_supervising_evaluation_option),"+++++++",select_supervising_evaluation_option)

		select_respect_evaluation_option = []

		if self.respect_ex == 1:
			select_respect_evaluation_option.append(self.respect_ex)
		if self.respect_vg == 1:
			select_respect_evaluation_option.append(self.respect_vg)
		if self.respect_go == 1:
			select_respect_evaluation_option.append(self.respect_go)
		if self.respect_wk == 1:
			select_respect_evaluation_option.append(self.respect_wk)
		if self.respect_vwk == 1:
			select_respect_evaluation_option.append(self.respect_vwk)
		print(len(select_respect_evaluation_option),"+++++++",select_respect_evaluation_option)

		if (len(select_work_environment_evaluation_option)>1 or len(select_salary_evaluation_option)>1 or len(select_treatment_evaluation_option)>1 or 
		len(select_work_training_evaluation_option)>1 or len(select_team_work_evaluation_option)>1 or len(select_communication_evaluation_option)>1 or 
		len(select_supervising_evaluation_option)>1 or len(select_respect_evaluation_option)>1):
			print("greater than 1 ------------------")
			frappe.throw(_("You cannot select multiple options in one row"))

		if (len(select_work_environment_evaluation_option)<1 or len(select_salary_evaluation_option)<1 or len(select_treatment_evaluation_option)<1 or 
		len(select_work_training_evaluation_option)<1 or len(select_team_work_evaluation_option)<1 or len(select_communication_evaluation_option)<1 or 
		len(select_supervising_evaluation_option)<1 or len(select_respect_evaluation_option)<1):
			print("less than 1 ------------------")
			frappe.throw(_("Please select any one option for every row"))
	
	def check_if_questions_answer_given_or_not(self):
		
		if (self.joining_yes == 0 and self.joining_no == 0):
			frappe.throw(_("Did you receive your Tasks on Joining ? <br>Please select Yes/No"))
		elif (self.work_yes == 0 and self.work_no == 0):
			frappe.throw(_("Do you wish to work with us Again ? <br>Please select Yes/No"))
		elif (self.department_yes == 0 and self.department_no == 0):
			frappe.throw(_("Do you wish to work for the same department Again ? <br>Please select Yes/No"))

		if (self.joining_yes == 1 and self.joining_no == 1) or (self.work_yes == 1 and self.work_no == 1) or (self.department_yes == 1 and self.department_no == 1):
			frappe.throw(_("You cannot select both. Please select <b>Yes</b> or <b>No</b>"))