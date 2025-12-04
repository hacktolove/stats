# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import get_link_to_form, cint, cstr
from frappe.model.document import Document

class InvalidDepartmentMergeError(frappe.ValidationError):
	pass

class AdministrativeStructureUpdatesRequestST(Document):
	
	# def validate(self):
	def on_submit(self):
		if self.request_type == "Create New Department":
			if self.type =="Create New Main Department":
				self.create_new_department(self.new_main_department_name,self.parent_department,self.main_department_manager)
			elif self.type == "Create New Sub Department":
				self.create_new_department(self.new_sub_department_name,self.parent_department,self.direct_manager
)
			elif self.type == "Create New Unit":
				self.create_new_employee_unit(self.new_employee_unit_name)
			
		elif self.request_type == "Merge Department":
			if self.type =="Merge Main Department":
				new_department_name = self.create_new_department(self.main_department_new_name,self.parent_department_name_1,self.new_main_department_manager)
				self.merge_department(self.existing_main_department_1,new_department_name)
				self.merge_department(self.existing_main_department_2,new_department_name)

			elif self.type == "Merge Sub Department":
				new_department_name = self.create_new_department(self.sub_department_new_name,self.parent_department_name_1,self.new_direct_manager)
				self.merge_department(self.existing_sub_department_1,new_department_name)
				self.merge_department(self.existing_sub_department_2,new_department_name)
			
			elif self.type == "Merge Unit":
				new_unit_name = self.create_new_employee_unit(self.new_unit_name)
				print(new_unit_name,"-----new unit",self.new_unit_name)
				self.merge_unit(self.existing_unit_1,new_unit_name)
				self.merge_unit(self.existing_unit_2,new_unit_name)

	def create_new_department(self,new_name,parent,manager):
		company = erpnext.get_default_company()
		department_doc = frappe.new_doc("Department")
		department_doc.department_name = new_name
		print(new_name,"-----------------------")
		if self.type in ["Create New Main Department","Merge Main Department"]:
			department_doc.custom_main_department_manager = manager
			department_doc.is_group = 1

		elif self.type in ["Create New Sub Department","Merge Sub Department"]:
			department_doc.custom_direct_manager = manager

		department_doc.parent_department = parent
		# department_doc.is_group = is_group
		department_doc.company = company
		department_doc.custom_task = self.task
		department_doc.custom_main_responsibilities = self.main_responsibilities
		department_doc.save(ignore_permissions=True)

		frappe.msgprint(_("New Main Department {0} Created".format(get_link_to_form("Department",department_doc.name))),alert=True)
		return department_doc.name

	def create_new_employee_unit(self,unit_name):
		employee_unit_doc = frappe.new_doc("Employee Unit ST")
		employee_unit_doc.employee_unit = unit_name
		employee_unit_doc.task = self.task
		employee_unit_doc.main_responsibilities = self.main_responsibilities
		print(unit_name,"unit name")
		employee_unit_doc.save(ignore_permissions=True)

		frappe.msgprint(_("New Employee Unit {0} Created".format(get_link_to_form("Employee Unit ST",employee_unit_doc.name))),alert=True)
		return employee_unit_doc.name

	def merge_department(self,old, new):
		# Validate properties before merging
		new_department = frappe.get_cached_doc("Department", new)
		old_department = frappe.get_cached_doc("Department", old)

		if not new_department:
			frappe.throw(_("Department {0} does not exist").format(new))

		if (
			cint(new_department.is_group),
			new_department.parent_department,
			new_department.company,
		) != (
			cint(old_department.is_group),
			old_department.parent_department,
			old_department.company,
		):
			frappe.throw(
				msg=_(
					"""Merging is only possible if following properties are same in both records. Is Group, Parent Department and Company"""
				),
				title=("Invalid Department"),
				exc=InvalidDepartmentMergeError,
			)

		if old_department.is_group and new_department.parent_department == old:
			new_department.db_set("parent_department", frappe.get_cached_value("Department", old, "parent_department"))

		frappe.rename_doc("Department", old, new, merge=1, force=1)

		frappe.msgprint(_("Two Departments are Merged as {0}".format(get_link_to_form("Department",new))),alert=True)
		return new
	
	def merge_unit(self,old, new):
		# Validate properties before merging
		new_unit = frappe.get_cached_doc("Employee Unit ST", new)
		old_unit = frappe.get_cached_doc("Employee Unit ST", old)

		if not new_unit:
			frappe.throw(_("Employee Unit {0} does not exist").format(new))

		frappe.rename_doc("Employee Unit ST", old, new, merge=1, force=1)

		frappe.msgprint(_("Two Units are Merged as {0}".format(get_link_to_form("Employee Unit ST",new))),alert=True)
		return new