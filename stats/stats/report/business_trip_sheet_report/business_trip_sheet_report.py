# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _,msgprint


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
			"fieldname": "business_trip_sheet_reference",
			"fieldtype": "Link",
			"label":_("Business Trip Sheet"),
			"options": "Business Trip Sheet ST",
			"width": 300
		},
		{
			"fieldname": "business_trip_request_reference",
			"fieldtype": "Link",
			"label":_("Business Trip Request Reference"),
			"options": "Business Trip Request ST",
			"width": 300
		},
		{
			"fieldname": "employee_no",
			"fieldtype": "Link",
			"label": _("Employee No"),
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
			"fieldname": "idresidency_number",
			"fieldtype": "Data",
			"label":_("ID/Residency No"),
			"width": 300
		},
		{
			"fieldname": "main_department",
			"fieldtype": "Link",
			"label":_("Main Department"),
			"options": "Department",
			"width": 200
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
			"width": 200
		},
		{
			"fieldname": "employee_salary",
			"fieldtype": "Currency",
			"label": _("Employee Salary"),
			"width": 200
		},
		{
			"fieldname": "trip_classification",
			"fieldtype": "Select",
			"label": _("Trip Classification"),
			"options": "Internal\nExternal",
			"width": 200
		},
		{
			"fieldname": "location",
			"fieldtype": "Data",
			"label": _("Location"),
			"width": 200
		},
		{
			"fieldname": "business_trip_start_date",
			"fieldtype": "Date",
			"label": _("Business Trip Start Date"),
			"width": 200
		},
		{
			"fieldname": "business_trip_end_date",
			"fieldtype": "Date",
			"label": _("Business Trip End Date"),
			"width": 200
		},
		{
			"fieldname": "approved_days",
			"fieldtype": "Int",
			"label":_("Approved Days"),
			"width": 200
		},
		{
			"fieldname": "per_diem_amount",
			"fieldtype": "Currency",
			"label": _("Per Diem Amount"),
			"width": 200
		},
		{
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"label":_("Total Amount"),
			"width": 200
		}
	]

	return columns

def get_data(filters):
	conditions = get_conditions(filters)

	business_trip_sheet_data = frappe.db.sql("""
							SELECT
								bts.name as business_trip_sheet_reference,
								ed.business_trip_reference as business_trip_request_reference,
								ed.employee_no,
								ed.employee_name,
								ed.main_department,
								ed.sub_department,
								e.grade,
								ed.approved_days,
								ed.business_trip_start_date,
								ed.business_trip_end_date,
								ed.total_amount,
								ed.employee_salary,
								e.custom_idresidency_number idresidency_number,
								btr.trip_classification,
								case 
									when (btr.trip_classification = 'External') then btr.country
									when (btr.trip_classification = 'Internal') then btr.saudi_city
								end as location,
								# btr.location,
								ed.per_diem_amount
							from
								`tabBusiness Trip Sheet ST` bts
							INNER JOIN `tabEmployee Details ST` ed ON
								ed.parent = bts.name
							INNER JOIN `tabBusiness Trip Request ST` btr ON 
								ed.business_trip_reference = btr.name
							INNER JOIN `tabEmployee` e ON
								e.name = ed.employee_no
							WHERE {0}
							ORDER BY bts.name 
					""".format(conditions),as_dict=True,debug=1)
	return business_trip_sheet_data

def get_conditions(filters):

	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "bts.date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
		else:
			frappe.throw(_("To Date should be greater then From Date"))
	if filters.get("business_trip_sheet_reference"):
		conditions += "and bts.name = '{0}'".format(filters.get("business_trip_sheet_reference"))	
	return conditions