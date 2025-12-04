# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import cstr

class EmployeeOnboardingST(Document):
	def on_submit(self):
		self.create_todo()

	def create_todo(self):
		for op in self.onboarding_procedures:
			if not op.todo:

				todo = frappe.new_doc('ToDo')
				todo.description = op.activity_name
				todo.custom_candidate_name = self.candidate_name
				todo.custom_candidate_namein_english = self.candidate_namein_english
				todo.custom_email = self.email
				todo.custom_phone_no = self.phone_no
				todo.reference_type = self.doctype
				todo.reference_name = self.name
				# todo.allocated_to = op.user
				# todo.custom_allocated_to_full_name = op.full_name
				todo.custom_send_email_notification_to = op.send_email_notification_to
				# todo.custom_direct_manager = op.direct_manager
				# todo.custom_direct_manager_full_name = op.direct_manager_full_name

				if op.company_email_creation_task == 1:
					todo.custom_create_company_email = 1

				todo.custom_technical_tools = op.technical_tools
				todo.custom_tool_1 = op.tool_1
				todo.custom_tool_2 = op.tool_2
				todo.custom_tool_3 = op.tool_3
				todo.custom_tool_4 = op.tool_4
				todo.custom_tool_5 = op.tool_5
				todo.custom_tool_6 = op.tool_6
				todo.custom_tool_7 = op.tool_7
				todo.custom_tool_8 = op.tool_8
				todo.custom_tool_9 = op.tool_9
				todo.custom_tool_10 = op.tool_10

				todo.run_method("set_missing_values")
				todo.save(ignore_permissions=True)

				frappe.db.set_value('Onboarding Procedures ST', op.name, 'todo', todo.name)
				frappe.msgprint(_("ToDo List Created: {0}").format(todo.name), alert=1)

@frappe.whitelist()
def get_onboarding_details(parent, parenttype):

	return frappe.get_all(
		"Employee Boarding Activity ST",
		fields=[
			"activity_name",
			"company_email_creation_task",
			"send_email_notification_to",
			"technical_tools",
			"tool_1", "tool_2", "tool_3", "tool_4",
			"tool_5", "tool_6", "tool_7", "tool_8",
			"tool_9", "tool_10"
		],
		filters={"parent": parent, "parenttype": parenttype},
		order_by="idx",
	)
