# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class ViolationST(Document):
	def validate(self):
		self.validate_penalty_details()
		self.check_all_penalty_recurrence_types_added_or_not()

	def validate_penalty_details(self):
		if len(self.penalty) > 1:
			recurrence=[]
			for row in self.penalty:
				if row.recurrence_type in recurrence:
						frappe.throw(_("In Penalty Table '{0}' Recurrence Type valid for one time only.").format(row.recurrence_type))
				else:
					recurrence.append(row.recurrence_type)

				if row.action_type == "Warning" and row.deduction and int(row.deduction) > 0:
					frappe.throw(_("In Row {0}: Deduction % Must be 0 when action type in Warning").format(row.idx))
				elif row.action_type == "Deduction" and int(row.deduction) <= 0:
					frappe.throw(_("In Row {0}: Deduction % Must be greater than 0 when action type in Deduction").format(row.idx))

	def check_all_penalty_recurrence_types_added_or_not(self):
		if len(self.penalty) > 1:
			recurrence_types = ["First Time", "Second Time", "Third Time", "Fourth Time"]
			for rec in recurrence_types:
				match_found = False
				for row in self.penalty:
					print(row.recurrence_type, '--row.recurrence_type')
					print(rec, '--rec')
					if row.recurrence_type == rec:
						match_found = True
						break
				if match_found == False:
					frappe.throw(_("Please Add Recurrence Type : {0}".format(rec)))
	


