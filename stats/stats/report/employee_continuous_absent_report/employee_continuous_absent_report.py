# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, get_time, today, cint, add_to_date, add_days, cstr
from erpnext.accounts.utils import get_fiscal_year
from frappe.core.doctype.role.role import get_users
# from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
from erpnext.setup.doctype.employee.employee import is_holiday
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
			"fieldname": "total_no_of_absent",
			"label":_("Total No of Absent"),
			"fieldtype": "Int",
			"width":"200"
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
	final_data = []

	result_data=frappe.db.sql("""
		SELECT
			e.employee,
			COUNT(a.attendance_date) as total_no_of_absent,
			e.first_name,
			e.custom_idresidency_number as idresidency_number,
			e.custom_section as section,
			e.department as main_department,
			e.custom_sub_department as sub_department,
			e.grade as employee_grade
		FROM
			`tabAttendance` a
		INNER JOIN `tabEmployee` e on e.name = a.employee
		WHERE a.status = "Absent" and {0} and e.employee NOT IN {1}
		GROUP BY e.employee
	""".format(conditions, emp), as_dict=1)

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
		WHERE a.status = "Absent" and {0}
		ORDER BY e.employee, a.attendance_date
	""".format(conditions), as_dict=1, debug=1 )

	if len(result_data)>0:
		for row in result_data:
			count_of_countinuous_absent = 0
			list_of_absent_dates = []
			next_absent_date = None
			if len(attendance_data)>0:
				for att in attendance_data:
					if row.employee == att.employee:
						if count_of_countinuous_absent == 5:
							break
						elif count_of_countinuous_absent < 6:
							if next_absent_date == None:
								next_absent_date = find_next_absent_date(att.employee,att.attendance_date)
								list_of_absent_dates.append(att.attendance_date)
								count_of_countinuous_absent += 1
							elif next_absent_date == att.attendance_date:
								list_of_absent_dates.append(att.attendance_date)
								count_of_countinuous_absent += 1
								next_absent_date = find_next_absent_date(att.employee,att.attendance_date)
							elif next_absent_date != att.attendance_date:
								next_absent_date = find_next_absent_date(att.employee,att.attendance_date)
								list_of_absent_dates = []
								list_of_absent_dates.append(att.attendance_date)
								count_of_countinuous_absent = 0
								count_of_countinuous_absent += 1
				dates = ", ".join((cstr(getdate(ele).day) if ele!=None else '') for ele in list_of_absent_dates)
				row["absent_date"] = dates
				if count_of_countinuous_absent >= 5:
					final_data.append(row)
				
	print("result_data", result_data)
	return final_data

def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		month = month_number_mapping.get(filters.get("month"))
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

def find_next_absent_date(employee, current_date):
	next_absent_date=add_days(current_date,1)
	is_off=is_holiday(employee,next_absent_date)
	print(is_off, "is_off")
	if is_off==False:
		return next_absent_date
	elif is_off==True:
		find_next_absent_date(employee,next_absent_date)