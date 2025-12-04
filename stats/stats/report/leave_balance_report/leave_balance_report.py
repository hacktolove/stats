# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	return [
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
			"fieldname": "idresidency_number",
			"fieldtype": "Data",
			"label":_("ID/Residency No"),
			"width": 300
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
			"fieldname": 'leave_type',
			"fieldtype": 'Link',
			"label": _('Leave Type'),
			"options": 'Leave Type',
			"width": 200
		},
		{
			"fieldname": "balance",
			"fieldtype": "Float",
			"label":_("Balance"),
			"width": 100
		}
	]

def get_data(filters):
	conditions=get_conditions(filters)
	year_start_date = filters.get("from_date")
	year_end_date = filters.get("to_date")
	employee_details = frappe.db.sql("""
						SELECT
							e.name as employee,
							e.employee_name,
							e.department as main_department,
							e.custom_sub_department as sub_department,
							e.custom_idresidency_number as idresidency_number,
							e.custom_contract_type as contract_type,
							ct.annual_leave_type as leave_type,
							ct.contract_type as contract,
							SUM(la.total_leave_days) as total_leave_days
						FROM
							`tabEmployee` e
						LEFT OUTER JOIN `tabContract Type ST` ct ON
							e.custom_contract_type = ct.name
						INNER JOIN `tabLeave Application` la ON
							la.employee = e.name 
						WHERE la.docstatus=1 and la.status='Approved' {0}
						GROUP BY e.name
					""".format(conditions),as_dict=True)
	if len(employee_details)>0:
		balance = 0
		for row in employee_details:
			allocated_days=frappe.db.get_value("Leave Allocation",
										{"from_date":["between",[year_start_date,year_end_date]],"to_date":["between",[year_start_date,year_end_date]],"leave_type":filters.get("leave_type"),"docstatus":1,"employee":row.employee},
										["total_leaves_allocated"])
			if allocated_days:
				balance = flt(allocated_days) - flt(row.total_leave_days)
				row["balance"]=balance
				
			
	return employee_details

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "and la.from_date between '{0}' and '{1}' and la.to_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
		else:
			frappe.throw(_("To Date should be greater then From Date"))
	if filters.get("employee"):
		conditions += "and la.employee = '{0}'".format(filters.get("employee"))	
	if filters.get("main_department"):
		conditions += " and e.department = '{0}'".format(filters.get("main_department"))
	if filters.get("sub_department"):
		conditions += " and e.custom_sub_department = '{0}'".format(filters.get("sub_department"))
	if filters.get("leave_type"):
		conditions += "and la.leave_type = '{0}'".format(filters.get("leave_type"))
	
	return conditions