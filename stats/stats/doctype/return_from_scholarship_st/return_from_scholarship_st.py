# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_to_date
from frappe.model.document import Document


class ReturnFromScholarshipST(Document):
	
	def validate(self):
		self.validate_return_date()

	def on_submit(self):
		self.delete_future_attendance_for_scholarship_return_date()

	def validate_return_date(self):
		if self.scholarship_end_date and self.return_date:
			if self.return_date <= self.scholarship_end_date:
				frappe.throw(_("Return Date cannot be less than or equal to Scholarship End Date"))
	
	def delete_future_attendance_for_scholarship_return_date(self):
		if self.return_date < self.plan_return_date:
			future_attendance_list = frappe.db.get_all("Attendance",
												filters={"employee":self.employee_no,"attendance_date":(">",self.return_date),"docstatus":1,"custom_attendance_type":"Scholarship"},
												fields=["name","attendance_date"])
			if len(future_attendance_list)>0:
				for row in future_attendance_list:
					attendance_doc = frappe.get_doc("Attendance",row.name)
					attendance_doc.cancel()
					attendance_doc.delete()
				frappe.msgprint(_("Future Attendance from {0} to {1} is deleted.").format(add_to_date(self.return_date,days=1),future_attendance_list[-1].attendance_date),alert=True)
			else:
				frappe.msgprint(_("No future attendance exists from {0}").format(add_to_date(self.return_date,days=1)),alert=True)