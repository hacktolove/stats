# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import datetime
from frappe import _
from frappe.model.document import Document
from hrms.hr.utils import validate_active_employee
from frappe.utils import get_link_to_form, getdate, cstr, get_datetime, nowdate
from frappe.utils.data import get_date_str
from stats.hr_utils import validate_dates, check_employee_in_salary_freezing, check_employee_in_scholarship, check_if_holiday_between_applied_dates


class AttendanceRequestST(Document):
	def validate(self):
		validate_active_employee(self.employee_no)
		validate_dates(self.employee_no, self.request_date, self.request_date)
		self.validate_request_overlap()
		self.validate_duplicate_record_for_employee_checkin()
		self.validate_employee_in_salary_freezing()
		self.validate_employee_in_scholarship()
		self.validate_is_holiday_exists()

	def on_submit(self):
		self.create_employee_checkin_records()
		self.check_in_or_out_and_cancel_attendance()
		
	def on_cancel(self):
		self.delete_employee_checkin_records()

	def validate_request_overlap(self):
		exists_request = frappe.db.exists("Attendance Request ST", {"request_date": self.request_date,"employee_no": self.employee_no,"attendance_type": self.attendance_type})
		if exists_request != None and exists_request != self.name:
			frappe.throw(_("This employee already has a request with the same date and attendance type <br><b>{0}</b>").format(get_link_to_form("Attendance Request ST", exists_request)))
	
	def create_employee_checkin_records(self):
		shift_name = frappe.db.get_value("Employee",self.employee_no,"default_shift")
		
		if shift_name:
			shift_start_time = frappe.db.get_value("Shift Type",shift_name,"start_time")
			shift_end_time = frappe.db.get_value("Shift Type",shift_name,"end_time")
		else:
			frappe.throw("Please set default shift in employee")

		employee_checkin_doc = frappe.new_doc("Employee Checkin")
		employee_checkin_doc.employee = self.employee_no
		employee_checkin_doc.log_type = self.attendance_type
		
		if self.attendance_type == "IN":
			employee_checkin_doc.time = get_datetime(get_date_str(self.request_date) + " " + cstr(shift_start_time))
		elif self.attendance_type == "OUT":
			employee_checkin_doc.time = get_datetime(get_date_str(self.request_date) + " " + cstr(shift_end_time))
		employee_checkin_doc.custom_reference_doctype = self.doctype
		employee_checkin_doc.custom_reference_docname = self.name
		employee_checkin_doc.custom_created_by_system = 1
		employee_checkin_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Employee Checkin is created <b>{0}</b>").format(get_link_to_form("Employee Checkin",employee_checkin_doc.name)),alert=True)

	def delete_employee_checkin_records(self):
		employee_checkin = frappe.db.get_all("Employee Checkin",
									   filters={"custom_reference_doctype":self.doctype,"custom_reference_docname":self.name},
									   fields=["name"])
		if len(employee_checkin)>0:
			for checkin in employee_checkin:
				employee_checkin_doc = frappe.get_doc("Employee Checkin",checkin.name)
				employee_checkin_doc.delete()
				frappe.msgprint(_("Employee Checkin <b>{0}</b> is deleted.").format(checkin.name),alert=True)

	def validate_employee_in_salary_freezing(self):
		exists_employee_salary_freezing = check_employee_in_salary_freezing(self.employee_no,from_date=self.request_date,to_date=None)
		if exists_employee_salary_freezing == True:
			frappe.throw(_("You cannot create Attendance Request as there is active salary freezing for employee {0}".format(self.employee_no)))

	def validate_employee_in_scholarship(self):
		exists_employee_scholarship = check_employee_in_scholarship(self.employee_no, from_date=self.request_date, to_date=None)
		if exists_employee_scholarship == True:
			frappe.throw(_("You cannot create Attendance Request as you have already apply for scholarship"))

	def validate_duplicate_record_for_employee_checkin(self):
		employee_checkin = frappe.db.get_all("Employee Checkin",
									   filters={"employee":self.employee_no,"log_type":self.attendance_type},
									   fields=["name","time"])
		
		if len(employee_checkin)>0:
			for ele in employee_checkin:
				if (getdate(ele.time) == getdate(self.request_date)):
					frappe.throw(_("This employee already has a employee checkin with the same date and attendance type <br><b>{0}</b>").format(get_link_to_form("Employee Checkin",ele.name)))

	def validate_is_holiday_exists(self):
		holiday_exists = check_if_holiday_between_applied_dates(self.employee_no,self.request_date,self.request_date,holiday_list=None)
		if holiday_exists == True:
			frappe.throw(_("You cannot create Attendance Request as there is holiday on {0}".format(getdate(self.request_date))))

	def check_in_or_out_and_cancel_attendance(self):
		if self.attendance_type == "IN":
			exist_out_record = frappe.db.get_all("Employee Checkin",
											filters={"time":["between",[self.request_date,self.request_date]],"employee":self.employee_no,"log_type":"OUT"},
											fields=["name","log_type"])
			if len(exist_out_record)>0:
				get_old_attendance = frappe.db.get_all("Attendance",
										   filters={"employee":self.employee_no,"attendance_date":self.request_date},
										   fields=["name"])
				if len(get_old_attendance)>0:
					attendance_doc = frappe.get_doc("Attendance",get_old_attendance[0].name)
					attendance_doc.cancel()
					attendance_doc.delete(ignore_permissions=True)

		if self.attendance_type == "OUT":
			exist_in_record = frappe.db.get_all("Employee Checkin",
											filters={"time":["between",[self.request_date,self.request_date]],"employee":self.employee_no,"log_type":"IN"},
											fields=["name","log_type"])
			if len(exist_in_record)>0:
				get_old_attendance = frappe.db.get_all("Attendance",
										   filters={"employee":self.employee_no,"attendance_date":self.request_date},
										   fields=["name"])
				if len(get_old_attendance)>0:
					attendance_doc = frappe.get_doc("Attendance",get_old_attendance[0].name)
					attendance_doc.cancel()
					attendance_doc.delete(ignore_permissions=True)			