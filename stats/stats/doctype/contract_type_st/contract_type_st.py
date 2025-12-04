# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ContractTypeST(Document):
	def validate(self):
		self.set_in_mins()
		# self.validate_salary_structure_percentage()
		self.validate_considered_vacation_days()

	def set_in_mins(self):
		self.total_mins_per_month=self.total_hours_per_month*60
		self.total_mins_per_day=self.total_hours_per_day*60
		
	def validate_salary_structure_percentage(self):
		field_name_of_total_monthly_salary='total_monthly_salary'
		if len(self.earning) > 0:
			total_monthly_salary = 100
			calculate_amount = 0

			for ear in self.earning:
					formula=ear.formula
					if formula  and formula.find(field_name_of_total_monthly_salary)>-1:
						amount = frappe.safe_eval(formula, None,{field_name_of_total_monthly_salary:total_monthly_salary})
						calculate_amount = calculate_amount + amount
					elif formula.find(field_name_of_total_monthly_salary) == -1:
						frappe.throw(_("In Row {0}: Please use correct variable 'total_monthly_salary' in formula.").format(ear.idx))

			if calculate_amount != total_monthly_salary:
				frappe.throw(_("Total of earnings must be 100%"))

	def validate_considered_vacation_days(self):
		if self.contract == "Civil" and self.considered_vacation_days > 180:
			frappe.throw(_("For Civil Contract: Vacation Days Cannot be Greater Than 180."))
		if self.contract == "Direct" and self.considered_vacation_days > 35:
			frappe.throw(_("For Direct Contract: Vacation Days Cannot be Greater Than 35."))