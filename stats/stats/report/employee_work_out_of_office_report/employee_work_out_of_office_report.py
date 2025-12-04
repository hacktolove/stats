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
			"fieldname": "deputy_employee_name",
			"fieldtype": "Data",
			"label":_("Deputy Employee Name"),
			"width": 300
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
					ew.employee_no,
					ew.employee_name,
					e.custom_section as section,
					ew.main_department,
					ew.sub_department,
					ew.from_date,
					ew.to_date,
					ew.no_of_days,
					ew.reasons,
					ew.deputy_employee_name,
					COUNT(dew.employee_no) as no_of_request
				FROM
					`tabEmployee Work Out of Office ST` as ew
				INNER JOIN `tabEmployee` as e ON
					e.name = ew.employee_no
				INNER JOIN `tabEmployee Work Out of Office ST` as dew
					ON ew.employee_no = dew.employee_no
					AND dew.docstatus =1 and {1}
				WHERE ew.docstatus =1 and {0}
				GROUP BY ew.name
			""".format(conditions, conditions_1),as_dict=True)
	return data

def get_conditions(filters):
	conditions = ""
	conditions_1 = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " ew.from_date between '{0}' and '{1}' and ew.to_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
		conditions_1 += " dew.from_date between '{0}' and '{1}' and dew.to_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))

	if filters.get("employee"):
		conditions += " and ew.employee_no = '{0}' ".format(filters.get("employee"))
	
	if filters.get("main_department"):
		conditions += " and ew.main_department = '{0}' ".format(filters.get("main_department"))

	if filters.get("sub_department"):
		conditions += " and ew.sub_department = '{0}' ".format(filters.get("sub_department"))
	
	if filters.get("section"):
		conditions += " and e.custom_section = '{0}' ".format(filters.get("section"))
	return conditions, conditions_1