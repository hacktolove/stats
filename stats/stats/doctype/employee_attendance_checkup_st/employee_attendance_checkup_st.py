# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from stats.hr_utils import check_employee_in_salary_freezing, check_employee_in_scholarship, check_if_holiday_between_applied_dates, check_employee_in_training
from frappe.utils import get_time

class EmployeeAttendanceCheckupST(Document):

	def validate(self):
		self.fetch_attendances()

	@frappe.whitelist()
	def fetch_attendances(self):
		employee_attendance_list = []

		if len(self.employee_attendance_checkup_details)>0:
			for row in self.employee_attendance_checkup_details:
				employee_checkin_time = {}
				get_employee_checkin = frappe.db.get_all("Employee Checkin",
											 filters={"employee":row.employee_no,"log_type":"IN","time":["between",[self.attendance_date,self.attendance_date]]},
											 fields=["name","time"])
				print(get_employee_checkin,"========================== get_employee_checkin")
				if len(get_employee_checkin)>0:
					for checkin in get_employee_checkin:
						if (get_time(checkin.time) <= get_time(self.attendance_to)) and (get_time(checkin.time) >= get_time(self.attendance_from)):
							employee_checkin_time["employee"]=row.employee_no
							employee_checkin_time["time"]=get_time(checkin.time)
							employee_attendance_list.append(employee_checkin_time)
		print(employee_attendance_list,"*******************************")
		return employee_attendance_list

	@frappe.whitelist()
	def fetch_employees(self):
		filters={"status":"Active"}

		if self.main_department:
			filters["department"]=self.main_department
		if self.sub_department:
			filters["custom_sub_department"]=self.sub_department
		if self.section:
			filters["custom_section"]=self.section
		if self.branch:
			filters["branch"]=self.branch

		active_employee_list = frappe.db.get_all("Employee",
										   filters=filters,
										   fields=["name"])
		final_list_of_employees = []
		if len(active_employee_list)>0:
			for employee in active_employee_list:
				check_employee_in_vacation = check_if_holiday_between_applied_dates(employee.name,self.attendance_date,self.attendance_date,holiday_list=None)
				if check_employee_in_vacation == True:
					continue
				else :
					check_employee_applied_for_scholarship = check_employee_in_scholarship(employee.name,self.attendance_date,to_date=None)
					if check_employee_applied_for_scholarship == True:
						continue
					else :
						check_if_employee_in_training = check_employee_in_training(employee.name,self.attendance_date,to_date=None)
						if check_if_employee_in_training == True:
							continue
						else :
							check_if_employee_in_salary_freezing = check_employee_in_salary_freezing(employee.name,self.attendance_date,to_date=None)
							if check_if_employee_in_salary_freezing == True:
								continue
							else :
								final_list_of_employees.append(employee)

		return final_list_of_employees