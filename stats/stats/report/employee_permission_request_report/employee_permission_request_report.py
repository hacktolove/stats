# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	return [
		{
			"fieldname": "employee_no",
			"label":_("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width":"200"
		},
		{
			"fieldname": "employee_name",
			"label":_("Employee Name"),
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
			"fieldname": "from_date",
			"label":_("From Date"),
			"fieldtype": "Date",
			"width":"235"
		},
		{
			"fieldname": "to_date",
			"label":_("To Date"),
			"fieldtype": "Date",
			"width":"235"
		},
		{
			"fieldname": "reasons",
			"label":_("Reason"),
			"fieldtype": "Data",
			"width":"235"
		},
		{
			"fieldname": "no_of_days",
			"label":_("No Of Days"),
			"fieldtype": "Int",
			"width":"235"
		},
		{
			"fieldname": "no_of_request",
			"label":_("No Of Request"),
			"fieldtype": "Int",
			"width":"235"
		},
	]

def get_data(filters):
	conditions, conditions_1 = get_conditions(filters)
	data = frappe.db.sql("""
				SELECT
					ep.employee_no,
					ep.employee_name,
					e.custom_section as section,
					ep.main_department,
					ep.sub_department,
					ep.from_date,
					ep.to_date,
					ep.no_of_days,
					ep.reasons,
					COUNT(dep.employee_no) as no_of_request
				FROM
					`tabEmployee Permission Request ST` as ep
				INNER JOIN `tabEmployee` as e ON
					e.name = ep.employee_no
				INNER JOIN `tabEmployee Permission Request ST` as dep
					ON ep.employee_no = dep.employee_no
					AND dep.docstatus =1 and {1}
				WHERE ep.docstatus =1 and {0}
				GROUP BY ep.name
				ORDER BY ep.employee_no  
			""".format(conditions, conditions_1),as_dict=True)
	return data

def get_conditions(filters):
	conditions = ""
	conditions_1 = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " ep.date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
		conditions_1 += " dep.date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))

	if filters.get("employee"):
		conditions += " and ep.employee_no = '{0}' ".format(filters.get("employee"))
	
	if filters.get("main_department"):
		conditions += " and ep.main_department = '{0}' ".format(filters.get("main_department"))

	if filters.get("sub_department"):
		conditions += " and ep.sub_department = '{0}' ".format(filters.get("sub_department"))
	
	if filters.get("section"):
		conditions += " and e.custom_section = '{0}' ".format(filters.get("section"))
	return conditions, conditions_1