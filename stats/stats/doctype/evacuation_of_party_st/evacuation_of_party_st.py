# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form


class EvacuationofPartyST(Document):
	def validate(self):
		if not self.resignation_reference and not self.retirement_reference:
			frappe.throw(_("Create Evacuation of Party from Employee Resignation/Retirement Doctype."))
		elif self.resignation_reference:
			resignation_status = frappe.db.get_value("Employee Resignation ST", self.resignation_reference, "docstatus")
			if resignation_status != 1:
				frappe.throw(_("Evacuation of Party can be created only for Submitted Employee Resignation."))
		elif self.retirement_reference:
			retirement_status = frappe.db.get_value("Retirement Request ST", self.retirement_reference, "docstatus")
			if retirement_status != 1:
				frappe.throw(_("Evacuation of Party can be created only for Submitted Employee Retirement."))

		self.set_tasks_level_wise_from_settings_doctype()
		self.check_already_exist_eop()
		self.validate_terms_and_conditions_read()

	def on_submit(self):
		if not self.evacuate_attachment:
			frappe.throw(_("Please attach evacuate proof"))

		self.check_all_levels_completed()

		resignation_doc = frappe.get_doc("Employee Resignation ST", self.resignation_reference)
		resignation_doc.employee_evacuation_status = "Processed"
		frappe.msgprint(_("In Employee Resignation: {0} Employee Evacuation Status Set to 'Processed'.").format(self.resignation_reference), alert=1)
		resignation_doc.add_comment("Comment",text="Employee Evacuation Status Set to <b>Processed</b> due to {0}".format(get_link_to_form(self.doctype,self.name)))
		resignation_doc.save(ignore_permissions=True)
	
	def on_trash(self):
		if self.resignation_reference:
			resignation_doc = frappe.get_doc("Employee Resignation ST", self.resignation_reference)
			resignation_doc.employee_evacuation_status = "Pending"
			frappe.msgprint(_("In Employee Resignation: {0} Employee Evacuation Status Set to 'Pending'.").format(self.resignation_reference), alert=1)
			resignation_doc.add_comment("Comment",text="Employee Evacuation Status Set to <b>Pending</b> due to delete {0} document".format(self.name))
			resignation_doc.save(ignore_permissions=True)

	def set_tasks_level_wise_from_settings_doctype(self):
		ss = frappe.get_doc('Stats Settings ST')
		
		if ss.first_level_task:
			self.first_level_task = ss.first_level_task

		if len(ss.evacuation_task_and_approval_second_level) > 0 and len(self.evacuation_second_level_tasks) < 1:
			for task in ss.evacuation_task_and_approval_second_level:
				second_tasks = self.append("evacuation_second_level_tasks", {})
				second_tasks.task_name = task.task_name
				second_tasks.in_charge_person = task.in_charge_person
				second_tasks.full_name = task.full_name
				second_tasks.status = "Pending"
				second_tasks.notes = task.notes

		if len(ss.evacuation_task_and_approval_third_level) > 0 and len(self.evacuation_third_level_tasks) < 1:
			for task in ss.evacuation_task_and_approval_third_level:
				third_tasks = self.append("evacuation_third_level_tasks", {})
				third_tasks.task_name = task.task_name
				third_tasks.in_charge_person = task.in_charge_person
				third_tasks.full_name = task.full_name
				# third_tasks.status = task.status
				third_tasks.status = "Pending"
				third_tasks.notes = task.notes

	def check_already_exist_eop(self):
		if self.resignation_reference:
			eop_exists = frappe.db.exists("Evacuation of Party ST",{"resignation_reference": self.resignation_reference, "name": ["!=", self.name]})
			if eop_exists:
				frappe.throw(_("Employee Evacuation For {0} Resignation Request is Already Done.").format(self.resignation_reference))
		
		elif self.retirement_reference:
			eop_exists = frappe.db.exists("Evacuation of Party ST",{"retirement_reference": self.retirement_reference, "name": ["!=", self.name]})
			if eop_exists:
				frappe.throw(_("Employee Evacuation For {0} Retirement Request is Already Done.").format(self.retirement_reference))
	
	def validate_terms_and_conditions_read(self):
		if self.terms_and_conditions:
			if self.i_agree_to_the_terms_and_conditions==0:
				frappe.throw(_("Please Read Terms & Conditions and check the checkbox below to conditions if agree with conditions"))
	
		
	def check_all_levels_completed(self):

		if self.fl_status == "Pending":
			frappe.throw(_("First Level Task is Pending."))

		if self.second_level_status == "Pending":
			frappe.throw(_("Second Level Task is Pending."))

		if len(self.evacuation_third_level_tasks) > 0:
			for task in self.evacuation_third_level_tasks:
				if task.status == "Pending":
					frappe.throw(_("Third Level Task is Pending."))

	@frappe.whitelist()
	def check_second_level_completed(self):
		level_completed = True

		for task in self.evacuation_second_level_tasks:
			if task.status == "Pending":
				level_completed = False
				break

		if level_completed:
			self.second_level_status = "Completed"
		else:
			self.second_level_status = "Pending"