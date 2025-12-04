# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from stats.hr_utils import get_no_of_day_between_dates


class OvertimeApprovalRequestST(Document):

	def validate(self):
		# self.deduct_vacation_and_absent_based_on_checkbox()
		self.validate_approved_no_of_days()
		
	def on_submit(self):
		self.check_approved_days_are_set()
	
	@frappe.whitelist()
	def deduct_vacation_and_absent_based_on_checkbox(self):
		overtime_doc = frappe.get_doc("Overtime Request ST",self.overtime_reference)
		if len(self.overtime_approval_employee_details)>0:
			for row in self.overtime_approval_employee_details:
				if row.deduct_vacation_and_absent_days == 1:
					no_of_vacation_days = 0
					if overtime_doc.day_type == "Week Days":
						leave_application_list = frappe.db.get_all("Leave Application",
									filters={"employee":row.employee_no,"docstatus":1},
									or_filters={"from_date":["between",[overtime_doc.overtime_start_date,overtime_doc.overtime_end_date]],"to_date":["between",[overtime_doc.overtime_start_date,overtime_doc.overtime_end_date]]},
									fields=["name"])
						if len(leave_application_list)>0:
							for la in leave_application_list:
								leave = frappe.get_doc("Leave Application",la.name)
								no_of_vacation_days = no_of_vacation_days + get_no_of_day_between_dates(overtime_doc.overtime_start_date,overtime_doc.overtime_end_date,leave.from_date,leave.to_date,row.employee_no)
									
						leave_outside_overtime_list = frappe.db.get_all("Leave Application",
									filters={"employee":row.employee_no,"docstatus":1,"from_date":["<",overtime_doc.overtime_start_date],"to_date":[">",overtime_doc.overtime_end_date]},
									fields=["name"])
						if len(leave_outside_overtime_list)>0:
							for ola in leave_outside_overtime_list:
								leave_doc = frappe.get_doc("Leave Application",ola.name)
								no_of_vacation_days = no_of_vacation_days + get_no_of_day_between_dates(overtime_doc.overtime_start_date,overtime_doc.overtime_end_date,leave_doc.from_date,leave_doc.to_date,row.employee_no)

					else:
						no_of_vacation_days = 0
					
					### get no of absent days from attendance

					no_of_absent_days = 0
					
					attendance_list = frappe.db.get_all("Attendance",
									filters={"employee":row.employee_no,"docstatus":1,"attendance_date":["between",[overtime_doc.overtime_start_date,overtime_doc.overtime_end_date]],"status":"Absent"},
									fields=["count(name) as total_absent_days"])
					if attendance_list[0].total_absent_days and attendance_list[0].total_absent_days > 0:
						no_of_absent_days = no_of_absent_days + attendance_list[0].total_absent_days
					
					expected_approved_days = (row.total_no_of_days or 0) - (no_of_vacation_days or 0) - (no_of_absent_days or 0)
				
				else : 
					no_of_vacation_days = 0
					no_of_absent_days = 0
					expected_approved_days = row.total_no_of_days

		return { "no_of_vacation":no_of_vacation_days, "no_of_absent":no_of_absent_days, "expected_approved_days":expected_approved_days }

	def check_approved_days_are_set(self):
		if len(self.overtime_approval_employee_details)>0:
			for row in self.overtime_approval_employee_details:
				if row.approved_days == None or row.approved_days == 0:
					frappe.throw(_("#Row {0}: Please set approve days".format(row.idx)))

	def validate_approved_no_of_days(self):
		if len(self.overtime_approval_employee_details)>0:
			for row in self.overtime_approval_employee_details:
				if row.approved_days:
					if row.approved_days > row.total_no_of_days or row.approved_days > row.expected_approved_days:
						frappe.throw(_("#Row {0}: Approved days cannot be greater than expected approved days".format(row.idx)))