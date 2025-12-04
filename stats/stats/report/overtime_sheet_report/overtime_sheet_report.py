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
			"fieldname": "overtime_sheet_reference",
			"fieldtype": "Link",
			"label":_("Overtime Sheet"),
			"options": "Overtime Sheet ST",
			"width": 300
		},
		{
			"fieldname": "overtime_request_reference",
			"fieldtype": "Link",
			"label":_("Overtime Request Reference"),
			"options": "Overtime Request ST",
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
			"fieldname": "grade",
			"fieldtype": "Link",
			"label":_("Grade"),
			"options":"Employee Grade",
			"width": 300
		},
		{
			"fieldname": "sub_department",
			"fieldtype": "Link",
			"label": _("Sub Department"),
			"options": "Department",
			"width": 200
		},
		{
			"fieldname": "transportation_amount",
			"fieldtype": "Currency",
			"label":_("Transportation Amount"),
			"width": 200
		},
		{
			"fieldname": "basic_salary",
			"fieldtype": "Currency",
			"label":_("Basic Salary"),
			"width": 200
		},
		{
			"fieldname": "total_salary",
			"fieldtype": "Currency",
			"label":_("Total Salary"),
			"width": 200
		},
		{
			"fieldname": "overtime_start_date",
			"fieldtype": "Date",
			"label":_("Overtime Start Date"),
			"width": 200
		},
		{
			"fieldname": "overtime_end_date",
			"fieldtype": "Date",
			"label":_("Overtime End Date"),
			"width": 200
		},
		{
			"fieldname": "required_days",
			"fieldtype": "Int",
			"label":_("Required Days"),
			"width": 200
		},
		{
			"fieldname": "no_of_hours_per_day",
			"fieldtype": "Float",
			"label":_("No of Hours Per Day"),
			"width": 200
		},
		{
			"fieldname": "day_type",
			"fieldtype": "Data",
			"label":_("Day Type"),
			"width": 200
		},
		{
			'fieldname' : 'no_of_vacation',
			'fieldtype' : 'Float',
			'label' : _('No of Vacation'),
			'width' : 150,
		},
		{
			'fieldname' : 'no_of_absent',
			'fieldtype' : 'Float',
			'label' : _('No of Absent'),
			'width' : 150,
		},
		{
			"fieldname": "total_no_of_approved_days",
			"fieldtype": "Int",
			"label":_("Total No Of Approved Days"),
			"width": 200
		},
		{
			"fieldname": "actual_extra_hours",
			"fieldtype": "Float",
			"label":_("Actual Extra Hours"),
			"width": 200
		},
		{
			"fieldname": "overtime_rate_per_hour",
			"fieldtype": "Currency",
			"label":_("Overtime Rate Per Hour"),
			"width": 200
		},
		{
			"fieldname": "transportation_rate",
			"fieldtype": "Currency",
			"label":_("Transportation Rate"),
			"width": 200
		},
		{
			"fieldname": "transportation_due_amount",
			"fieldtype": "Currency",
			"label":_("Transportation Due Amount"),
			"width": 200
		},
		{
			"fieldname": "amount",
			"fieldtype": "Currency",
			"label":_("Amount"),
			"width": 200
		},
		{
			"fieldname": "status",
			"fieldtype": "Data",
			"label":_("Status"),
			"width": 200,
			"default": "Approved"
		}
	]

	return columns

def get_data(filters):
	conditions = get_conditions(filters)

	overtime_sheet_data = frappe.db.sql("""
							SELECT
								os.name as overtime_sheet_reference,
								osed.overtime_request_reference,
								osed.employee_no ,
								osed.employee_name,
								osed.required_days ,
								osed.total_no_of_approved_days ,
								osed.actual_extra_hours ,
								osed.overtime_rate_per_hour ,
								osed.amount,
								osed.total_salary,
								osed.basic_salary,
								osed.transportation_amount,
								ors.overtime_start_date,
								ors.overtime_end_date,
								osed.no_of_hours_per_day,
								ors.day_type,
								osed.transport_per_day transportation_rate,
								e.grade,
								e.custom_idresidency_number as idresidency_number,
								e.custom_sub_department as sub_department, 
								osed.no_of_vacation,
								osed.no_of_absent,
								(osed.transport_per_day * osed.total_no_of_approved_days) transportation_due_amount,
								'Approved' as status
							FROM
								`tabOvertime Sheet ST` os
							INNER JOIN `tabOvertime Sheet Employee Details ST` osed ON
								osed.parent = os.name
							INNER JOIN `tabOvertime Request ST` ors ON
								ors.name = osed.overtime_request_reference
							INNER JOIN `tabEmployee Overtime Request Details ST` eord ON
								eord.parent = ors.name
							LEFT OUTER JOIN `tabEmployee` e ON
								e.name = osed.employee_no
							WHERE {0}
							GROUP BY e.name, ors.name
							ORDER BY os.name
					""".format(conditions),as_dict=True,debug=1)
	
	return overtime_sheet_data

def get_conditions(filters):

	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "os.creation_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
		else:
			frappe.throw(_("To Date should be greater then From Date"))
	if filters.get("overtime_sheet_reference"):
		conditions += "and os.name = '{0}'".format(filters.get("overtime_sheet_reference"))	
	return conditions