# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document
from stats.api import set_degree_based_on_weight,validate_weight


class EmployeePersonalGoalsST(Document):

	def validate(self):
		self.validate_length()
		self.validate_duplicate_entry_of_employee_based_on_fiscal_year()
		set_degree_based_on_weight(self.personal_goals)
		validate_weight(self.personal_goals)
		set_degree_based_on_weight(self.job_goals)
		validate_weight(self.job_goals)

	def validate_length(self):
		if len(self.personal_goals)>4:
			frappe.throw(_("You cannot add more than 4 Goals"))

	def validate_duplicate_entry_of_employee_based_on_fiscal_year(self):
		if self.employee_no and self.fiscal_year:
			exists_personal_goal = frappe.db.exists("Employee Personal Goals ST", {"employee_no": self.employee_no,"fiscal_year":self.fiscal_year})
			if exists_personal_goal != None and exists_personal_goal != self.name:
				frappe.throw(_("You cannot create employee personal goal for fiscal year {0} and employee {1} again").format(self.fiscal_year,self.employee_no))