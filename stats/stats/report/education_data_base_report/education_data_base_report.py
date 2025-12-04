# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		frappe.msgprint(_("No records found"))
		return columns, data
	
	return columns, data

def get_columns(filters):
	columns = [
		{
			"fieldname": "request_ref",
			"fieldtype": "Link",
			"label": _("Request Ref"),
			"options": "Education Allowance Request ST",
			"width": 130
		},
		{
			"fieldname": "educational_year",
			"fieldtype": "Link",
			"label": _("Educational Year"),
			"options": "Educational Year ST",
			"width": 140
		},
		{
			"fieldname": "idresidency_number",
			"fieldtype": "Data",
			"label":_("ID/Residency No"),
			"width": 150
		},
		{
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"label": _("Employee Name"),
			"width": 250
		},
		{
			"fieldname": "sub_department",
			"fieldtype": "Link",
			"label":_("Sub Department"),
			"options": "Department",
			"width": 200
		},
		{
			"fieldname": "grade",
			"fieldtype": "Link",
			"label": _("Grade"),
			"options": "Employee Grade",
			"width": 120
		},
		{
			"fieldname": "kid_name",
			"fieldtype": "Data",
			"label": _("Kid Name"),
			"width": 150
		},
		{
			"fieldname": "kid_id",
			"fieldtype": "Data",
			"label": _("Kid ID"),
			"width": 150
		},
		{
			"fieldname": "kid_age",
			"fieldtype": "Data",
			"label": _("Kid Age"),
			"width": 100
		},
		{
			"fieldname": "request_date",
			"fieldtype": "Date",
			"label": _("Request Date"),
			"width": 150
		},
		{
			"fieldname": "school_name",
			"fieldtype": "Data",
			"label": _("School Name"),
			"width": 200
		},
		{
			"fieldname": "season_type",
			"fieldtype": "Data",
			"label": _("Season Type"),
			"width": 150
		},
		{
			"fieldname": "approved_amount",
			"fieldtype": "Currency",
			"label":_("Approved Amount"),
			"width": 150
		},
		{
			"fieldname": "due_amount",
			"fieldtype": "Currency",
			"label":_("Due Amount"),
			"width": 150
		}
		
	]
	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "er.creation_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
		else:
			frappe.throw(_("To Date should be greater then From Date"))

	if filters.get("employee_id"):
		conditions += "and er.employee_no = '{0}'".format(filters.get("employee_id"))

	if filters.get("sub_department"):
		conditions += "and er.sub_department = '{0}'".format(filters.get("sub_department"))

	if filters.get("eduction_year"):
		conditions += "and er.educational_year = '{0}'".format(filters.get("eduction_year"))

	return conditions

def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql("""
			SELECT 
				er.name as request_ref,
				er.educational_year as educational_year, 
				emp.custom_idresidency_number as idresidency_number,
				er.employee_name as employee_name, 
				er.sub_department as sub_department, 
				er.grade as grade,
				erd.child_name as kid_name,
				erd.id_number as kid_id,
				erd.age as kid_age,
				er.creation_date as request_date,
				erd.school_name as school_name,
				erd.season_type as season_type,
				erd.approved_amount as approved_amount,
				erd.ed_due_amount as due_amount
			FROM
				`tabEducation Allowance Request ST` as er
			INNER JOIN `tabEducation Allowance Request Details ST` as erd ON
				erd.parent = er.name
			INNER JOIN `tabEmployee` as emp ON
				emp.name = er.employee_no 
			WHERE {0}
			""".format(conditions),as_dict=True,debug=1)
	
	return data
