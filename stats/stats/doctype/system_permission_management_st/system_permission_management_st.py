# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form


class SystemPermissionManagementST(Document):

	# def validate(self):
	# 	self.validate_designation()
	# 	self.validate_main_department_manager()
	# 	self.validate_sub_department_direct_manager()

	# def on_submit(self):
	# 	self.change_designation_in_employee_profileI()
	# 	self.change_main_department_manager()
	# 	self.change_sub_department_direct_manager()

	def validate_designation(self):
		if self.old_designation and self.new_designation:
			if self.new_designation == self.old_designation:
				frappe.throw(_("You cannot select Designation <b>{0}</b>".format(self.new_designation)))

	def validate_main_department_manager(self):
		if self.main_department_manager_old and self.main_department_manager_new:
			if self.main_department_manager_new == self.main_department_manager_old:
				frappe.throw(_("You cannot select Manager <b>{0}</b>".format(self.main_department_manager_new)))

	def validate_sub_department_direct_manager(self):
		if self.old_direct_manager and self.new_direct_manager:
			if self.old_direct_manager == self.new_direct_manager:
				frappe.throw(_("You cannot select Direct Manager <b>{0}</b>".format(self.new_direct_manager)))

	def change_designation_in_employee_profileI(self):
		if self.employee_for_designation and self.new_designation:
			employee_doc = frappe.get_doc("Employee",self.employee_for_designation)
			employee_doc.designation = self.new_designation
			employee_doc.add_comment("Comment",text="Designation is changed to {0} due to {1}".format(self.new_designation,get_link_to_form("System Permission Management ST",self.name)))
			employee_doc.save(ignore_permissions = True)
			frappe.msgprint(_("Designation is changed in Employee {0}".format(get_link_to_form("Employee",self.employee_for_designation))),alert=True)

	def change_main_department_manager(self):
		if self.main_department_manager_new:
			department_doc = frappe.get_doc("Department",self.main_department)
			department_doc.custom_main_department_manager = self.main_department_manager_new
			department_doc.add_comment("Comment",text="Main Department Manager is changed to {0} due to {1}".format(self.main_department_manager_new,get_link_to_form("System Permission Management ST",self.name)))
			department_doc.save(ignore_permissions = True)
			frappe.msgprint(_("Main Department Manager is changed in Department {0}".format(get_link_to_form("Department",self.main_department))),alert=True)

	def change_sub_department_direct_manager(self):
		if self.new_direct_manager:
			sub_department_doc = frappe.get_doc("Department",self.sub_department)
			sub_department_doc.custom_direct_manager = self.new_direct_manager
			sub_department_doc.add_comment("Comment",text="Direct Manager is changed to {0} due to {1}".format(self.new_direct_manager,get_link_to_form("System Permission Management ST",self.name)))
			sub_department_doc.save(ignore_permissions = True)
			frappe.msgprint(_("Direct Manager is changed in Department {0}".format(get_link_to_form("Department",self.sub_department))),alert=True)