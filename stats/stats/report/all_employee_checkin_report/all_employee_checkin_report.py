# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _
from frappe.core.doctype.role.role import get_users


def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_("No records found"))
		return columns, data
	
	return columns, data

def get_conditions(filters):
	conditions =""

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "DATE(att.attendance_date) between {0} and {1}".format(
        		frappe.db.escape(filters.get("from_date")),
        		frappe.db.escape(filters.get("to_date")))		
		else:
			frappe.throw(_("To Date should be greater then From Date"))	

	if filters.employee:
		conditions += " and att.employee = '{0}'".format(filters.employee)

	if filters.section:
		conditions += " and emp.custom_section = '{0}'".format(filters.section)
	
	if filters.main_department:
		conditions += " and emp.department = '{0}'".format(filters.main_department)

	if filters.sub_department:
		conditions += " and emp.custom_sub_department = '{0}'".format(filters.sub_department)

	return conditions

def get_columns(filters):
	columns = [
		{
			"fieldname": "employee",
			"fieldtype": "Link",
			"label": _("Employee ID"),
			"options": "Employee",
			"width": 200
		},
		{
			"fieldname": "employee_number",
			"fieldtype": "Data",
			"label": _("Employee Number"),
			"width": 200
		},
		{
			"fieldname": "first_name",
			"fieldtype": "Data",
			"label": _("First Name"),
			"width": 200
		},
		{
			"fieldname": "attendance_date",
			"fieldtype": "Date",
			"label": _("Date"),
			"width": 200
		},
		{
			"fieldname": "attendance_day",
			"fieldtype": "Data",
			"label": _("Day"),
			"width": 200
		},
		{
			"fieldname": "residency_number",
			"fieldtype": "Data",
			"label": _("ID/Residency Number"),
			"width": 200
		},
		{
			"fieldname": "designation",
			"fieldtype": "Link",
			"label": _("Designation"),
			"options": "Designation",
			"width": 200
		},
		{
			"fieldname": "section",
			"fieldtype": "Link",
			"label": _("Section"),
			"options": "Section ST",
			"width": 200
		},
		{
			"fieldname": "main_department",
			"label":_("Main Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": 200
		},
		{
			"fieldname": "sub_department",
			"label":_("Sub Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": 200
		},
		{
			"fieldname": "checkin_reference",
			"label":_("Checkin Reference"),
			"fieldtype": "Link",
			"options": "Employee Checkin",
			"width": 200
		},
		{
			"fieldname": "in_time",
			"fieldtype": "Data",
			"label": _("Time In"),
			"width": 200
		},
		{
			"fieldname": "out_time",
			"fieldtype": "Data",
			"label": _("Time Out"),
			"width": 200
		},
		{
			"fieldname": "in_device",
			"fieldtype": "Data",
			"label": _("In Device"),
			"width": 200
		},
		{
			"fieldname": "out_device",
			"fieldtype": "Data",
			"label": _("Out Device"),
			"width": 200
		},
		{
			"fieldname": "actual_working_hours",
			"fieldtype": "Data",
			"label": _("Actual Working Hours"),
			"width": 200
		},
		{
			"fieldname": "required_working_hours",
			"fieldtype": "Data",
			"label": _("Required Working Hours"),
			"width": 200
		},
		{
			"fieldname": "extra_working_hours",
			"fieldtype": "Data",
			"label": _("Extra Working Hours"),
			"width": 200
		},
		# {
		# 	"fieldname": "late_in",
		# 	"fieldtype": "Data",
		# 	"label": _("Late In (mins)"),
		# 	"width": 200
		# },
		# {
		# 	"fieldname": "early_out",
		# 	"fieldtype": "Data",
		# 	"label": _("Early Out (mins)"),
		# 	"width": 200
		# },
		{
			"fieldname": "attendance",
			"label":_("Attendance"),
			"fieldtype": "Link",
			"options": "Attendance",
			"width": 200
		}
	]

	return columns

def get_data(filters):
	role = frappe.db.get_single_value("Stats Settings ST","attendance_hide_role")
	user_list = get_users(role)
	employee_list = []
	if len(user_list) > 0:
		for user in user_list:
			employee = frappe.db.exists("Employee",{"user_id":user})
			if employee:
				employee_list.append(employee)

	if len(employee_list)>0:
		emp=tuple(employee_list) if len(employee_list)>1 else (employee_list[0],"")
	else:
		emp=("","")
	conditions = get_conditions(filters)

	data = frappe.db.sql(""" 
		SELECT 
			att.employee as employee, 
			emp.employee_number as employee_number, 
			emp.first_name as first_name, 
			emp.custom_idresidency_number as residency_number, 
			emp.designation as designation, 
			emp.custom_section as section, 
			emp.department as main_department, 
			emp.custom_sub_department as sub_department,
			DAYNAME(att.attendance_date) as attendance_day, 
			att.attendance_date as attendance_date,
			CASE 
				when es.log_type='IN' then es.time
			END as in_time,
			CASE 
				when es.log_type='OUT' then es.time
			END as out_time,
			CONCAT(FLOOR(att.custom_actual_working_minutes/60),'h ',MOD(att.custom_actual_working_minutes,60),'m') as actual_working_hours,
			CONCAT(FLOOR(att.custom_working_minutes_per_day/60),'h ',MOD(att.custom_working_minutes_per_day,60),'m')  as required_working_hours,
			CONCAT(FLOOR(att.custom_extra_minutes/60), 'h ',MOD(att.custom_extra_minutes,60),'m') as extra_working_hours,
			# att.custom_actual_delay_minutes as late_in,
			# att.custom_actual_early_minutes as early_out,
			att.name as attendance,
			es.name as checkin_reference,
			CASE 
				when di.log_type='IN' then di.name
			END as in_device,
			CASE 
				when di.log_type='OUT' then di.name
			END as out_device
		FROM tabAttendance as att 
			INNER JOIN tabEmployee as emp ON 
				emp.name = att.employee
			LEFT OUTER JOIN `tabEmployee Checkin` as es ON
				att.name = es.attendance
			LEFT OUTER JOIN `tabDevice ID ST` as di ON
				es.device_id = di.name
		WHERE {0} and att.employee NOT IN {1}
		ORDER BY att.employee, att.attendance_date ASC 
 		""".format(conditions, emp),filters, as_dict=1,debug=1)
	# if len(data) > 0:
	# 	for d in data:
	# 		checkin_list = frappe.db.get_all("Employee Checkin",
	# 								filters={"attendance":d.name},
	# 								fields=["device_id","log_type"])
	# 		if len(checkin_list) > 0:
	# 			for checkin in checkin_list:
	# 				if checkin.log_type == "IN":
	# 					d["in_device"] = frappe.db.get_value("Device ID ST", checkin.device_id, "device_name")
	# 				if checkin.log_type == "OUT":
	# 					d["out_device"] = frappe.db.get_value("Device ID ST", checkin.device_id, "device_name")

	return data