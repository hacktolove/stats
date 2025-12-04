# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.utils import date_diff, add_to_date, getdate
from erpnext.setup.doctype.employee.employee import is_holiday
from frappe.core.doctype.role.role import get_users
from stats.hr_utils import get_no_of_day_between_dates

def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_attendance_data(filters)

	return columns, data

def get_columns(filters):
	return [
		{
			"fieldname": "employee",
			"label":_("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width":"200"
		},
		{
			"fieldname": "employee_number",
			"label":_("Employee Number"),
			"fieldtype": "Data",
			"width":"150"
		},
		{
			"fieldname": "first_name",
			"label":_("First Name"),
			"fieldtype": "Data",
			"width":"200"
		},
		{
			"fieldname": "idresidency_number",
			"label":_("ID/Residency Number"),
			"fieldtype": "Data",
			"width":"200"
		},
		{
			"fieldname": "designation",
			"label":_("Designation"),
			"fieldtype": "Link",
			"options": "Designation",
			"width":"200"
		},
		{
			"fieldname": "section",
			"label":_("Section"),
			"fieldtype": "Link",
			"options": "Section ST",
			"width":"200"
		},
		{
			"fieldname": "main_department",
			"label":_("Main Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width":"200"
		},
		{
			"fieldname": "sub_department",
			"label":_("Sub Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width":"200"
		},
		{
			"fieldname": "no_of_present",
			"label":_("No of Present"),
			"fieldtype": "Int",
			"width":"150"
		},
		{
			"fieldname": "no_of_absent",
			"label":_("No of Absent"),
			"fieldtype": "Int",
			"width":"150"
		},
		# {
		# 	"fieldname": "no_of_delay",
		# 	"label":_("No of Delay"),
		# 	"fieldtype": "Int",
		# 	"width":"100"
		# },
		{
			"fieldname": "no_of_permission",
			"label":_("No of Permission"),
			"fieldtype": "Int",
			"width":"150"
		},
		{
			"fieldname": "no_of_work_out_of_office",
			"label":_("No of  Work out of Office"),
			"fieldtype": "Int",
			"width":"150"
		},
		{
			"fieldname": "no_of_attendance_request",
			"label":_("No of Attendance Request"),
			"fieldtype": "Int",
			"width":"200"
		},
		{
			"fieldname": "no_breastfeeding_permission",
			"label":_("No BreastFeeding Permission"),
			"fieldtype": "Int",
			"width":"150"
		},
		{
			"fieldname": "absent_percentage",
			"label":_("Absent %"),
			"fieldtype": "Percent",
			"width":"150"
		},
		# {
		# 	"fieldname": "delay_percentage",
		# 	"label":_("Delay %"),
		# 	"fieldtype": "Percent",
		# 	"width":"150"
		# },
		{
			"fieldname": "permission_percentage",
			"label":_("Permission %"),
			"fieldtype": "Percent",
			"width":"150"
		},
		{
			"fieldname": "remote_work_percentage",
			"label":_("Remote Work %"),
			"fieldtype": "Percent",
			"width":"150"
		},
		{
			"fieldname": "breastfeeding_percentage",
			"label":_("Breastfeeding %"),
			"fieldtype": "Percent",
			"width":"150"
		},
		{
			"fieldname": "work_out_office_percentage",
			"label":_("Work out Office %"),
			"fieldtype": "Percent",
			"width":"150"
		}
	]

def get_attendance_data(filters):
	role = frappe.db.get_single_value("Stats Settings ST","attendance_hide_role")
	user_list = get_users(role)
	employee_list = []
	if len(user_list) > 0:
		for user in user_list:
			employee = frappe.db.exists("Employee",{"user_id":user})
			if employee:
				employee_list.append(employee)
	print(user_list, "-------------user_list")
	print(employee_list,"-----employee")
	if len(employee_list)>0:
		emp=tuple(employee_list) if len(employee_list)>1 else (employee_list[0],"")
	else:
		emp=("","")
	print(emp, type(emp), "+++++++++++++++++")
	
	conditions = get_conditions(filters)
	attendance_data = frappe.db.sql("""
		SELECT
			e.employee,
			e.employee_number,
			e.first_name,
			e.custom_idresidency_number as idresidency_number,
			e.designation,
			e.custom_section as section,
			e.department as main_department,
			e.custom_sub_department as sub_department
		FROM
			`tabAttendance` a
		INNER JOIN `tabEmployee` e on e.name = a.employee
		WHERE {0} and e.employee NOT IN {1}
		GROUP BY e.name
	""".format(conditions,emp), as_dict=1)
	print(conditions,"------------")
	print(attendance_data,"=======attendance_data")
	report_from_date = getdate(filters.get("from_date"))
	report_to_date = getdate(filters.get("to_date"))
	if len(attendance_data)>0:
		for row in attendance_data:

			no_of_present = frappe.db.get_all("Attendance", filters={"employee": row["employee"], "status": "Present", "attendance_date":["between",[filters.get("from_date"),filters.get("to_date")]]}, fields=["count(name) as no_of_present"])
			if len(no_of_present)>0:
				if no_of_present[0].no_of_present:
					row["no_of_present"] = no_of_present[0].no_of_present
				else:
					row["no_of_present"] = 0

			no_of_absent = frappe.db.get_all("Attendance", filters={"employee": row["employee"], "status": "Absent", "attendance_date":["between",[filters.get("from_date"),filters.get("to_date")]]}, fields=["count(name) as no_of_absent"])
			if len(no_of_absent)>0:
				if no_of_absent[0].no_of_absent:
					row["no_of_absent"] = no_of_absent[0].no_of_absent
				else:
					row["no_of_absent"] = 0
			
			# no_of_delay = frappe.db.get_all("Attendance", filters={"employee": row["employee"], "late_entry": 1, "attendance_date":["between",[filters.get("from_date"),filters.get("to_date")]]}, fields=["count(name) as no_of_delay"])
			# if len(no_of_delay)>0:
			# 	if no_of_delay[0].no_of_delay:
			# 		row["no_of_delay"] = no_of_delay[0].no_of_delay
			# 	else:
			# 		row["no_of_delay"] = 0

			no_of_permission = frappe.db.get_all("Employee Permission Request ST", filters={"employee_no": row["employee"], "docstatus": 1, "request_date":["between",[filters.get("from_date"),filters.get("to_date")]]}, fields=["count(name) as no_of_permission"])
			if len(no_of_permission)>0:
				if no_of_permission[0].no_of_permission:
					row["no_of_permission"] = no_of_permission[0].no_of_permission
				else:
					row["no_of_permission"] = 0

			no_of_work_out_of_office = frappe.db.get_all("Employee Work Out of Office ST", filters={"employee_no": row["employee"], "docstatus": 1, "from_date":["between",[filters.get("from_date"),filters.get("to_date")]], "to_date":["between",[filters.get("from_date"),filters.get("to_date")]]}, fields=["count(name) as no_of_work_out_of_office"])
			if len(no_of_work_out_of_office)>0:
				if no_of_work_out_of_office[0].no_of_work_out_of_office:
					row["no_of_work_out_of_office"] = no_of_work_out_of_office[0].no_of_work_out_of_office
				else:
					row["no_of_work_out_of_office"] = 0
			
			total_no_of_attendance_request = frappe.db.get_all("Attendance Request", filters={"employee": row["employee"], "docstatus": 1,"reason":"Work From Home", "from_date":["between",[filters.get("from_date"),filters.get("to_date")]], "to_date":["between",[filters.get("from_date"),filters.get("to_date")]]}, fields=["count(name) as total_no_of_attendance_request"])
			if len(total_no_of_attendance_request)>0:
				if total_no_of_attendance_request[0].total_no_of_attendance_request:
					row["no_of_attendance_request"] = total_no_of_attendance_request[0].total_no_of_attendance_request
				else:
					row["no_of_attendance_request"] = 0

			# attendance_request_list = frappe.db.get_all("Attendance Request", 
			# 									filters={"employee": row["employee"], "docstatus": 1, "reason":"Work From Home"},
			# 									or_filters={"from_date":["between",[filters.get("from_date"),filters.get("to_date")]], "to_date":["between",[filters.get("from_date"),filters.get("to_date")]]}, 
			# 									fields=["from_date","to_date","custom_work_from_home_days"])
			# total_no_of_attendance_request_days = 0
			# if len(attendance_request_list)>0:
			# 	for request in attendance_request_list:
			# 		total_no_of_attendance_request_days = total_no_of_attendance_request_days + get_no_of_day_between_dates(report_from_date, report_to_date, request.from_date, request.to_date,row.employee_no)
					
			# attendance_request_list_outside_date = frappe.db.get_all("Attendance Request",
			# 									filters={"employee": row["employee"], "docstatus": 1, "reason":"Work From Home", "from_date":["<",report_from_date], "to_date":[">",report_to_date]},
			# 									fields=["from_date","to_date","custom_work_from_home_days"])
			# if len(attendance_request_list_outside_date)>0:
			# 	for attendance_data in attendance_request_list_outside_date:
			# 		total_no_of_attendance_request_days = total_no_of_attendance_request_days + get_no_of_day_between_dates(report_from_date, report_to_date, attendance_data.from_date, attendance_data.to_date,row.employee_no)

			# row["no_of_attendance_request"] = total_no_of_attendance_request_days or 0
			
			# breastfeeding_permission_list = frappe.db.get_all("Employee Breast Feeding Request ST", 
			# 										  filters={"employee_no": row["employee"], "docstatus": 1},
			# 										  or_filters={"from_date":["between",[filters.get("from_date"),filters.get("to_date")]], "to_date":["between",[filters.get("from_date"),filters.get("to_date")]]},
			# 										  fields=["from_date","to_date","total_no_of_days"])
			# total_no_of_breastfeeding_days = 0
			# if len(breastfeeding_permission_list)>0:
			# 	for record in breastfeeding_permission_list:
			# 		total_no_of_breastfeeding_days = total_no_of_breastfeeding_days + get_no_of_day_between_dates(report_from_date, report_to_date, record.from_date, record.to_date,row.employee_no)

			# breastfeeding_permission_list_outside_date = frappe.db.get_all("Employee Breast Feeding Request ST", 
			# 										  filters={"employee_no": row["employee"], "docstatus": 1,"from_date":["<",report_from_date], "to_date":[">",report_to_date]},
			# 										  fields=["from_date","to_date","total_no_of_days"])
			# if len(breastfeeding_permission_list_outside_date)>0:
			# 	for data in breastfeeding_permission_list_outside_date:
			# 		total_no_of_breastfeeding_days = total_no_of_breastfeeding_days + get_no_of_day_between_dates(report_from_date, report_to_date, data.from_date, data.to_date,row.employee_no)
			total_no_of_breastfeeding_request = frappe.db.get_all("Employee Breast Feeding Request ST", filters={"employee_no": row["employee"], "docstatus": 1,"from_date":["between",[filters.get("from_date"),filters.get("to_date")]], "to_date":["between",[filters.get("from_date"),filters.get("to_date")]]}, fields=["count(name) as total_no_of_breastfeeding_request"])
			if len(total_no_of_breastfeeding_request)>0:
				if total_no_of_breastfeeding_request[0].total_no_of_breastfeeding_request:
					row["no_breastfeeding_permission"] = total_no_of_breastfeeding_request[0].total_no_of_breastfeeding_request
				else:
					row["no_breastfeeding_permission"] = 0
					
			# row["no_breastfeeding_permission"] = total_no_of_breastfeeding_days or 0
			row["absent_percentage"] = (row["no_of_absent"]/30)*100 if row["no_of_absent"] else 0
			# row["delay_percentage"] = (row["no_of_delay"]/30)*100 if row["no_of_delay"] else 0
			row["permission_percentage"] = (row["no_of_permission"]/30)*100 if row["no_of_permission"] else 0
			row["remote_work_percentage"] = (row["no_of_attendance_request"]/30)*100 if row["no_of_attendance_request"] else 0
			row["breastfeeding_percentage"] = (row["no_breastfeeding_permission"]/30)*100 if row["no_breastfeeding_permission"] else 0
			row["work_out_office_percentage"] = (row["no_of_work_out_of_office"]/30)*100 if row["no_of_work_out_of_office"] else 0

	return attendance_data

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " a.attendance_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
	if filters.get("employee"):
		conditions += " and e.name = '{0}'".format(filters.get("employee"))
	if filters.get("main_department"):
		conditions += " and e.department = '{0}'".format(filters.get("main_department"))
	if filters.get("sub_department"):
		conditions += " and e.custom_sub_department = '{0}'".format(filters.get("sub_department"))
	if filters.get("section"):
		conditions += " and e.custom_section = '{0}'".format(filters.get("section"))

	return conditions