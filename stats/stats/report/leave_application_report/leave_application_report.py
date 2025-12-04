# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _,msgprint
from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on

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
			"fieldname": "leave_reference",
			"fieldtype": "Link",
			"label":_("Leave Reference"),
			"options": "Leave Application",
			"width": 300
		},
		{
			"fieldname": "leave_request_reference",
			"fieldtype": "Link",
			"label":_("Leave Request Reference"),
			"options": "Leave Request ST",
			"width": 300
		},
		{
			"fieldname": "employee",
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
			"fieldname": "contract_type",
			"fieldtype": "Link",
			"label": _("Contract Type"),
			"options": "Contract Type ST",
			"width": 200
		},
		{
			"fieldname": "contract",
			"fieldtype": "Select",
			"label": _("Contract"),
			"options": "Civil\nDirect",
			"width": 200
		},
		{
			"fieldname": "employee_number",
			"fieldtype": "Data",
			"label": _("Employee Number"),
			"width": 200
		},
		{
			"fieldname": "after_leave_balance",
			"fieldtype": "Data",
			"label": _("After Leave Balance"),
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
			"fieldname": "section",
			"fieldtype": "Link",
			"label": _("Section"),
			"options": "Section ST",
			"width": 200
		},
		{
			"fieldname": 'workflow_state',
			"fieldtype": 'Link',
			"label": _('Workflow Status'),
			"options": 'Workflow State',
			"width": 300
		},
		{
			"fieldname": 'status',
			"fieldtype": 'Select',
			"label": _('Status'),
			"options": 'Open\nApproved\nRejected\nCancelled\nPending',
			"width": 200
		},
		{
			"fieldname": 'leave_type',
			"fieldtype": 'Link',
			"label": _('Leave Type'),
			"options": 'Leave Type',
			"width": 200
		},
		{
			"fieldname": "no_of_days",
			"fieldtype": "Int",
			"label":_("No Of Days"),
			"width": 100
		},
		{
			"fieldname": "deputy_employee_name",
			"fieldtype": "Data",
			"label":_("Deputy Employee Name"),
			"width": 300
		},
		{
			"fieldname": "leave_start_date",
			"fieldtype": "Date",
			"label":_("Leave Start Date"),
			"width": 200
		},
		{
			"fieldname": "leave_end_date",
			"fieldtype": "Date",
			"label":_("Leave End Date"),
			"width": 200
		},
		{
			"fieldname": "leave_request_date",
			"fieldtype": "Date",
			"label":_("Leave Request Date"),
			"width": 200
		}
	]

	return columns

def get_data(filters):
	conditions, conditions_2 = get_conditions(filters)

	leave_application_list = frappe.db.sql("""
							SELECT
								la.name as leave_reference,
								la.employee,
								la.employee_name ,
								e.custom_idresidency_number as idresidency_number,
								la.workflow_state,
								la.status,
								la.leave_type,
								la.total_leave_days as no_of_days,
								la.from_date as leave_start_date,
								la.to_date as leave_end_date,
								la.posting_date as leave_request_date,
								la.custom_deputy_employee_name deputy_employee_name,
								e.custom_section as section,
								e.department as main_department,
								e.custom_sub_department as sub_department,
								e.custom_contract_type as contract_type, 
								e.employee_number,
								cts.contract
							FROM
								`tabLeave Application` la
							INNER JOIN `tabEmployee` e ON
								e.name = la.employee 
							INNER JOIN `tabContract Type ST` cts ON
								cts.name = 	e.custom_contract_type	
							WHERE la.docstatus != 2 {0}
					""".format(conditions),as_dict=True, debug=1)
	print(leave_application_list,"-----------leave_application_list")
	
	leave_request_list = frappe.db.sql("""
							SELECT
								lr.name as leave_request_reference,
								lr.employee_no as employee,
								lr.employee_name,
								lr.main_department,
								lr.sub_department,
								e.custom_idresidency_number as idresidency_number,
								e.custom_section as section,
								lr.leave_type,
								lr.total_no_of_days as no_of_days,
								lr.from_date as leave_start_date,
								lr.to_date as leave_end_date,
								lr.status,
								lr.deputy_employee_name,
								lr.workflow_state,
								e.custom_contract_type as contract_type,
								e.employee_number,
								cts.contract	 
							FROM
								`tabLeave Request ST` lr
							INNER JOIN `tabEmployee` e ON
								e.name = lr.employee_no
							INNER JOIN `tabContract Type ST` cts ON
								cts.name = 	e.custom_contract_type	
							WHERE
								lr.docstatus = 0 {0}
					""".format(conditions_2), as_dict=True, debug=1)
	print(leave_request_list, "------------leave_request_list")
	
	leave_report_data = leave_application_list + leave_request_list
	
	for d in leave_report_data:
		curr_balance = get_leave_balance_on(d['employee'], d['leave_type'], d['leave_start_date'], d['leave_end_date'], True)
		d['after_leave_balance'] = round(curr_balance, 2)
	return leave_report_data

def get_conditions(filters):

	conditions = ""
	conditions_2 = ""
	if filters.get("employee"):
		conditions += "and la.employee = '{0}'".format(filters.get("employee"))	
		conditions_2 += "and lr.employee_no = '{0}'".format(filters.get("employee"))
	if filters.get("main_department"):
		conditions += " and e.department = '{0}'".format(filters.get("main_department"))
		conditions_2 += " and lr.main_department = '{0}'".format(filters.get("main_department"))
	if filters.get("sub_department"):
		conditions += " and e.custom_sub_department = '{0}'".format(filters.get("sub_department"))
		conditions_2 += " and lr.sub_department = '{0}'".format(filters.get("sub_department"))
	if filters.get("section"):
		conditions += " and e.custom_section = '{0}'".format(filters.get("section"))
		conditions_2 += " and e.custom_section = '{0}'".format(filters.get("section"))
	if filters.get("workflow_status"):
		conditions += "and la.workflow_state = '{0}'".format(filters.get("workflow_status"))
		conditions_2 += "and lr.workflow_state = '{0}'".format(filters.get("workflow_status"))
	if filters.get("leave_application_status"):
		conditions += "and la.status = '{0}'".format(filters.get("leave_application_status"))
	if filters.get("leave_request_status"):
		conditions_2 += "and lr.status = '{0}'".format(filters.get("leave_request_status"))
	if filters.get("leave_type"):
		conditions += "and la.leave_type = '{0}'".format(filters.get("leave_type"))
		conditions_2 += "and lr.leave_type = '{0}'".format(filters.get("leave_type"))
	if filters.get("contract"):
		conditions += "and cts.contract = '{0}'".format(filters.get("contract"))
		conditions_2 += "and cts.contract = '{0}'".format(filters.get("contract"))
	return conditions, conditions_2