# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form

class GeneralStructureChangeRequestST(Document):
	def on_submit(self):
		self.change_value_in_department()

	def change_value_in_department(self):
		if self.change_level_type == "Second Level and Over":
			department_doc = frappe.get_doc("Department",self.main_department)
			if self.new_task:
				department_doc.custom_task = self.new_task
				department_doc.add_comment("Comment",text="Task is changed due to {0}".format(get_link_to_form("General Structure Change Request ST",self.name)))
				frappe.msgprint(_("Task is changed in Department {0}".format(get_link_to_form("Department",self.main_department))),alert=True)

			if self.new_stake_holders:
				department_doc.custom_stake_holders = self.new_stake_holders
				department_doc.add_comment("Comment",text="Stake Holders is changed due to {0}".format(get_link_to_form("General Structure Change Request ST",self.name)))
				frappe.msgprint(_("Stake Holders is changed in Department {0}".format(get_link_to_form("Department",self.main_department))),alert=True)

			if self.new_main_responsibilities:
				department_doc.custom_main_responsibilities = self.new_main_responsibilities
				department_doc.add_comment("Comment",text="Main Responsibilities is changed due to {0}".format(get_link_to_form("General Structure Change Request ST",self.name)))
				frappe.msgprint(_("Main Responsibilities is changed in Department {0}".format(get_link_to_form("Department",self.main_department))),alert=True)
			
			department_doc.save(ignore_permissions = True)
		
		if self.change_level_type == "Third Level and Below":
			department_doc = frappe.get_doc("Department",self.sub_department)
			if self.new_task:
				department_doc.custom_task = self.new_task
				department_doc.add_comment("Comment",text="Task is changed due to {0}".format(get_link_to_form("General Structure Change Request ST",self.name)))
				frappe.msgprint(_("Task is changed in Department {0}".format(get_link_to_form("Department",self.sub_department))),alert=True)

			if self.new_stake_holders:
				department_doc.custom_stake_holders = self.new_stake_holders
				department_doc.add_comment("Comment",text="Stake Holders is changed due to {0}".format(get_link_to_form("General Structure Change Request ST",self.name)))
				frappe.msgprint(_("Stake Holders is changed in Department {0}".format(get_link_to_form("Department",self.sub_department))),alert=True)

			if self.new_main_responsibilities:
				department_doc.custom_main_responsibilities = self.new_main_responsibilities
				department_doc.add_comment("Comment",text="Main Responsibilities is changed due to {0}".format(get_link_to_form("General Structure Change Request ST",self.name)))
				frappe.msgprint(_("Main Responsibilities is changed in Department {0}".format(get_link_to_form("Department",self.sub_department))),alert=True)
			
			department_doc.save(ignore_permissions = True)