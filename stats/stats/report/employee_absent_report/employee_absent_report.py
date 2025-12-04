# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, get_time
from frappe.core.doctype.role.role import get_users


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
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
			"fieldname": "employee_grade",
			"label":_("Employee Grade"),
			"fieldtype": "Link",
			"options": "Employee Grade",
			"width":"200"
		},
		{
			"fieldname": "absent_date",
			"label":_("Absent Date"),
			"fieldtype": "Data",
			"width":"235"
		},
		{
			"fieldname": "no_of_days",
			"label":_("No Of Days"),
			"fieldtype": "Int",
			"width":"235"
		}
	]

def get_data(filters):
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
	conditions = get_conditions(filters)
	month = getdate("09-04-2025").month
	print(month,"======================")
	attendance_data = frappe.db.sql("""
		SELECT
			e.employee,
			a.attendance_date,
			e.first_name,
			e.custom_idresidency_number,
			e.designation,
			e.custom_section,
			e.department,
			e.custom_sub_department,
			e.grade
		FROM
			`tabAttendance` a
		INNER JOIN `tabEmployee` e on e.name = a.employee
		WHERE a.status = "Absent" and {0} and e.employee NOT IN {1}
	""".format(conditions, emp), as_dict=1)
	print(conditions,"------------")
	updated_data = []
	employee_list = []
	if len(attendance_data)>0:
		for ele in attendance_data:
			if ele.employee not in employee_list:
				absent_date = ""
				no_of_days = 0
				for row in attendance_data:
					if ele.employee == row.employee:
						ab_date = getdate(row.attendance_date).day
						no_of_days = no_of_days + 1
						if absent_date == "":
							absent_date = str(ab_date)
						else:
							absent_date = str(absent_date) + "," + str(ab_date)
				new_row = {}
				new_row["employee"] = ele.employee
				new_row["first_name"] = ele.first_name
				new_row["idresidency_number"] = ele.custom_idresidency_number
				new_row["section"] = ele.custom_section
				new_row["main_department"] = ele.department
				new_row["sub_department"] = ele.custom_sub_department
				new_row["employee_grade"] = ele.grade
				new_row["absent_date"] = absent_date
				new_row["no_of_days"]=no_of_days
				updated_data.append(new_row)
				employee_list.append(ele.employee)
			else:
				pass

	return updated_data

def get_conditions(filters):

	month_number_mapping = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
		}
	conditions = ""
	if filters.get("month"):
		month = month_number_mapping.get(filters.get("month"))
		print(month,"----------------")
		conditions += "MONTH(a.attendance_date) = '{0}' ".format(month)
	if filters.get("employee"):
		conditions += " and e.name = '{0}'".format(filters.get("employee"))
	if filters.get("main_department"):
		conditions += " and e.department = '{0}'".format(filters.get("main_department"))
	if filters.get("sub_department"):
		conditions += " and e.custom_sub_department = '{0}'".format(filters.get("sub_department"))
	if filters.get("section"):
		conditions += " and e.custom_section = '{0}'".format(filters.get("section"))
	return conditions