# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EmployeeOnboardingTemplateST(Document):
	def validate(self):
		self.validate_company_email_creation_task()
		# self.set_direct_manager()

	def validate_company_email_creation_task(self):
		if len(self.activities) > 0:
			for act1 in self.activities:
				if act1.company_email_creation_task == 1:
					for act2 in self.activities:
						if act2.company_email_creation_task == 1 and act2.name != act1.name:
							frappe.throw(_("Company Email Creation Task Should be one time only."))

	# def set_direct_manager(self):
	# 	if len(self.activities) > 0:
	# 		for act in self.activities:
	# 			if act.user:
	# 				emp, emp_name = frappe.db.get_value('Employee', {'user_id': act.user}, ['name', 'employee_name'])
	# 				act.direct_manager = emp or ''
	# 				act.direct_manager_full_name = emp_name or ''
