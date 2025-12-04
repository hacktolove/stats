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
			"fieldname": "checkin_reference",
			"label":_("Checkin Reference"),
			"fieldtype": "Link",
			"options": "Employee Checkin",
			"width": 200
		},
		{
			"fieldname": "in_device",
			"fieldtype": "Data",
			"label": _("In Device"),
			"width": 200
		},
		{
			"fieldname": "checkin_time",
			"fieldtype": "Data",
			"label": _("Checkin Time"),
			"width": 200
		},
		{
			"fieldname": "checkout_reference",
			"label":_("Checkout Reference"),
			"fieldtype": "Link",
			"options": "Employee Checkin",
			"width": 200
		},
		{
			"fieldname": "out_device",
			"fieldtype": "Data",
			"label": _("Out Device"),
			"width": 200
		},
		{
			"fieldname": "checkout_time",
			"fieldtype": "Data",
			"label": _("Checkout Time"),
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
		},
		{
			"fieldname": "attendance_status",
			"label":_("Attendance Status"),
			"fieldtype": "Select",
			"options": "Present\nAbsent\nOn Leave\nOn LWP\nIn Training\nBusiness Trip\nScholarship\nPresent Due To Reconciliation\nHalf Day\nWork From Home",
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

select 
	att.employee as employee, 
	emp.employee_number as employee_number, 
	emp.first_name as first_name, 
	att.attendance_date as attendance_date,
	DAYNAME(att.attendance_date) as attendance_day, 
	emp.custom_idresidency_number as residency_number, 
	emp.designation as designation, 
	emp.custom_section as section, 
	emp.department as main_department, 
	emp.custom_sub_department as sub_department,
	att.in_time as in_time, 
	att.out_time as out_time,
	att.custom_attendance_type as attendance_status,
	CONCAT(FLOOR(att.custom_actual_working_minutes/60),'h ',MOD(att.custom_actual_working_minutes,60),'m') as actual_working_hours,
	CONCAT(FLOOR(att.custom_working_minutes_per_day/60),'h ',MOD(att.custom_working_minutes_per_day,60),'m')  as required_working_hours,
	CONCAT(FLOOR(att.custom_extra_minutes/60), 'h ',MOD(att.custom_extra_minutes,60),'m') as extra_working_hours,
	# att.custom_actual_delay_minutes as late_in,
	# att.custom_actual_early_minutes as early_out,
	att.name as attendance,
	checkin.in_device as in_device,		
	checkin.name as checkin_reference,
	checkin.time as checkin_time,		
	checkout.out_device as out_device,	
	checkout.name as checkout_reference,
	checkout.time as checkout_time				
from tabAttendance as att 
INNER JOIN tabEmployee as emp ON emp.name = att.employee
left outer join
(
	select 
		tec.attendance, tec.time , tec.device_id, tec.name,IFNULL(di.device_name,"No device set") as in_device,
		ROW_NUMBER() OVER (PARTITION BY tec.attendance ORDER BY tec.time) rn 
	from `tabEmployee Checkin` tec  
			LEFT OUTER JOIN `tabDevice ID ST` as di ON
			tec.device_id = di.name
			where tec.log_type = 'IN'
) checkin on checkin.attendance = att.name and checkin.rn = 1
left outer join
(
	select 
		tec.attendance, tec.time , tec.device_id, tec.name,IFNULL(di.device_name,"No device set") as out_device,
		ROW_NUMBER() OVER (PARTITION BY tec.attendance ORDER BY tec.time DESC) rn 
	from `tabEmployee Checkin` tec 
			LEFT OUTER JOIN `tabDevice ID ST` as di ON
			tec.device_id = di.name	
			where tec.log_type = 'OUT' 
) checkout on checkout.attendance = att.name and checkout.rn = 1
where {0} and att.employee NOT IN {1}				
 		""".format(conditions, emp),filters, as_dict=1,debug=1)
	return data