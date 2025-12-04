# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _

def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_("No records found"))
		return columns, data
	
	return columns, data

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
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"label": _("Employee Name"),
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
			"fieldname": "reason",
			"fieldtype": "Data",
			"label": _("Reason"),
			"width": 200
		},
		{
			"fieldname": "request_date",
			"fieldtype": "Date",
			"label": _("Request Date"),
			"width": 200
		},
		{
			"fieldname": "total_no_of_request",
			"fieldtype": "Data",
			"label": _("Total No of Request"),
			"width": 200
		},
	]
	return columns

def get_conditions(filters):
	conditions =""

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "DATE(ar.creation) between {0} and {1}".format(
        		frappe.db.escape(filters.get("from_date")),
        		frappe.db.escape(filters.get("to_date")))		
		else:
			frappe.throw(_("To Date should be greater then From Date"))

	if filters.employee:
		conditions += " and emp.name = '{0}'".format(filters.employee)

	if filters.section:
		conditions += " and emp.custom_section = '{0}'".format(filters.section)
	
	if filters.main_department:
		conditions += " and emp.department = '{0}'".format(filters.main_department)

	if filters.sub_department:
		conditions += " and emp.custom_sub_department = '{0}'".format(filters.sub_department)
	
	return conditions


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(""" SELECT 
			emp.name as employee, 
			emp.employee_name as employee_name, 
			emp.custom_section as section, 
			emp.department as main_department,
			emp.custom_sub_department as sub_department,
			ar.reason as reason,
			DATE(ar.creation) as request_date,
			COUNT(ar.name) as total_no_of_request 
			From `tabAttendance Request` as ar 
			INNER JOIN `tabEmployee` as emp ON emp.name = ar.employee
			WHERE {0}
			GROUP BY emp.name """.format(conditions),filters, as_dict=1)
	return data