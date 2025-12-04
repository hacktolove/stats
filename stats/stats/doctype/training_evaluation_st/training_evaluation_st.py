# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TrainingEvaluationST(Document):
	def validate(self):
		if not self.is_new():
			self.not_allow_to_select_multiple_evaluation_option()

	def not_allow_to_select_multiple_evaluation_option(self):
		achieving_the_goals_of_the_program_training_list = ["achieving_the_goals_of_the_program_training_ex","achieving_the_goals_of_the_program_training_vg","achieving_the_goals_of_the_program_training_go","achieving_the_goals_of_the_program_training_ac","achieving_the_goals_of_the_program_training_wk"]
		adapting_content_to_business_needs_list = ["adapting_content_to_business_needs_ex","adapting_content_to_business_needs_vg","adapting_content_to_business_needs_go","adapting_content_to_business_needs_ac","adapting_content_to_business_needs_wk"]
		clarity_and_organization_of_scientific_material_list = ["clarity_and_organization_of_scientific_material_ex","clarity_and_organization_of_scientific_material_vg","clarity_and_organization_of_scientific_material_go","clarity_and_organization_of_scientific_material_ac","clarity_and_organization_of_scientific_material_wk"]
		diversity_of_presentation_and_explanation_methods_list = ["diversity_of_presentation_and_explanation_methods_ex","diversity_of_presentation_and_explanation_methods_vg","diversity_of_presentation_and_explanation_methods_go","diversity_of_presentation_and_explanation_methods_ac","diversity_of_presentation_and_explanation_methods_wk"]
		the_trainer_mastered_the_scientific_material_list = ["the_trainer_mastered_the_scientific_material_ex","the_trainer_mastered_the_scientific_material_vg","the_trainer_mastered_the_scientific_material_go","the_trainer_mastered_the_scientific_material_ac","the_trainer_mastered_the_scientific_material_wk"]
		delivery_and_communication_style_list = ["delivery_and_communication_style_ex","delivery_and_communication_style_vg","delivery_and_communication_style_go","delivery_and_communication_style_ac","delivery_and_communication_style_wk"]
		ability_to_motivate_trainees_list = ["ability_to_motivate_trainees_ex","ability_to_motivate_trainees_vg","ability_to_motivate_trainees_go","ability_to_motivate_trainees_ac","ability_to_motivate_trainees_wk"]
		effective_time_management_list = ["effective_time_management_ex","effective_time_management_vg","effective_time_management_go","effective_time_management_ac","effective_time_management_wk"]
		organizing_the_workshop_and_the_schedule_list = ["organizing_the_workshop_and_the_schedule_ex","organizing_the_workshop_and_the_schedule_vg","organizing_the_workshop_and_the_schedule_go","organizing_the_workshop_and_the_schedule_ac","organizing_the_workshop_and_the_schedule_wk"]
		suitability_of_the_workshop_location_list = ["suitability_of_the_workshop_location_ex","suitability_of_the_workshop_location_vg","suitability_of_the_workshop_location_go","suitability_of_the_workshop_location_ac","suitability_of_the_workshop_location_wk"]
		support_list = ["support_ex","support_vg","support_go","support_ac","support_wk"]

		self.common_for_evaluation_option(achieving_the_goals_of_the_program_training_list)
		self.common_for_evaluation_option(adapting_content_to_business_needs_list)
		self.common_for_evaluation_option(clarity_and_organization_of_scientific_material_list)
		self.common_for_evaluation_option(diversity_of_presentation_and_explanation_methods_list)
		self.common_for_evaluation_option(the_trainer_mastered_the_scientific_material_list)
		self.common_for_evaluation_option(delivery_and_communication_style_list)
		self.common_for_evaluation_option(ability_to_motivate_trainees_list)
		self.common_for_evaluation_option(effective_time_management_list)
		self.common_for_evaluation_option(organizing_the_workshop_and_the_schedule_list)
		self.common_for_evaluation_option(suitability_of_the_workshop_location_list)
		self.common_for_evaluation_option(support_list)

	def common_for_evaluation_option(self, field_list):
		select_evaluation_option = []

		if len(field_list) > 0:
			for field in field_list:
				if self.get(field) == 1:
					select_evaluation_option.append(self.get(field))

		if len(select_evaluation_option) > 1:
			frappe.throw(_("You cannot select multiple evaluation options in one row. Please select only one."))
		elif len(select_evaluation_option) < 1:
			frappe.throw(_("Please select at least one evaluation option."))
