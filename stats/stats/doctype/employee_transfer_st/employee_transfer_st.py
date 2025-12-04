# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days


class EmployeeTransferST(Document):
	def on_submit(self):
		employee = frappe.get_doc("Employee", self.employee_no)
		employee.custom_sub_department=self.new_sub_department
		employee.department=self.new_main_department
		employee.custom_section=self.new_section
		employee.reports_to = self.new_direct_manager

		if not employee.custom_stats_employee_internal_work_history:
			employee.append(
					"custom_stats_employee_internal_work_history",
					{
						"main_department": self.main_department,
						"sub_department": self.sub_department,
						"section":self.section,
						"from_date": employee.date_of_joining
					},
				)
		custom_stats_employee_internal_work_history={
						"main_department":self.new_main_department,
						"sub_department": self.new_sub_department,
						"section":self.new_section,
						"from_date": self.transfer_date,
		}
		employee.append("custom_stats_employee_internal_work_history", custom_stats_employee_internal_work_history)
		update_to_date_in_work_history(employee,cancel=False)
		employee.save()

	def on_cancel(self):
		employee = frappe.get_doc("Employee", self.employee_no)
		employee.custom_sub_department=self.sub_department
		employee.department=self.main_department
		employee.custom_section=self.section
		employee.reports_to = self.direct_manager

		if employee.custom_stats_employee_internal_work_history:
			for row in employee.custom_stats_employee_internal_work_history:
				if row.from_date == self.transfer_date and row.sub_department == self.new_sub_department and row.main_department == self.new_main_department:
					employee.custom_stats_employee_internal_work_history.remove(row)
					break
		update_to_date_in_work_history(employee, cancel=True)

		employee.save()
def update_to_date_in_work_history(employee, cancel):
	if not employee.custom_stats_employee_internal_work_history:
		return

	for idx, row in enumerate(employee.custom_stats_employee_internal_work_history):
		if not row.from_date or idx == 0:
			continue

		prev_row = employee.custom_stats_employee_internal_work_history[idx - 1]
		if not prev_row.to_date:
			prev_row.to_date = add_days(row.from_date, -1)

	if cancel:
		employee.custom_stats_employee_internal_work_history[-1].to_date = None
