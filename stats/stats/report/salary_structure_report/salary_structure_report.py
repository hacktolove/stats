# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if not filters: filters = {}

	earnings = frappe.db.sql_list("SELECT tsd.salary_component FROM `tabSalary Detail` tsd INNER JOIN `tabSalary Component` tsc ON tsc.name = tsd.salary_component WHERE tsc.type = 'Earning' GROUP BY tsd.salary_component")

	deduction = frappe.db.sql_list("SELECT tsd.salary_component FROM `tabSalary Detail` tsd INNER JOIN `tabSalary Component` tsc ON tsc.name = tsd.salary_component WHERE tsc.type = 'Deduction' GROUP BY tsd.salary_component")
	columns, data = [], []

	columns = get_columns(earnings, deduction)
	data = get_data(filters, earnings, deduction)

	return columns, data

def get_columns(earnings, deduction):
	columns = [
		{
			"fieldname": "id",
			"label":_("ID"),
			"fieldtype": "Link",
			"options": "Salary Structure",
			"width":'300'
		},
		{
			"fieldname": "is_active",
			"label":_("Is Active"),
			"fieldtype": "Data",
			"width":'100'
		},
		{
			"fieldname": "employee_no",
			"label":_("Employee No"),
			"fieldtype": "Link",
			"options": "Employee",
			"width":'200'
		},
		{
			"fieldname": "employee_name",
			"label":_("Employee Name"),
			"fieldtype": "Data",
			"width":'300'
		},
		{
			"fieldname": "iD_residency_number",
			"label":_("ID/Residency Number"),
			"fieldtype": "Data",
			"width":'150'
		},
	]

	for col in earnings:
		columns.append(
				{
				"fieldname": _(col),
				"label":_(col),
				"fieldtype": "Currency",
				"width":'160'
			})
	
	columns.append(
			{
				"fieldname": "total_earnings",
				"label":_("Total Earnings"),
				"fieldtype": "Currency",
				"width":'200'
			})
		
	for col in deduction:
		columns.append(
				{
				"fieldname": _(col),
				"label":_(col),
				"fieldtype": "Currency",
				"width":'160'
			})
		
	columns.append(
			{
				"fieldname": "total_deduction",
				"label":_("Total Deduction"),
				"fieldtype": "Currency",
				"width":'200'
			})
	
	columns.append({
				"fieldname": "net_amount",
				"label":_("Net Amount"),
				"fieldtype": "Currency",
				"width":'200'
			})

	return columns


def get_conditions(filters):
	print(filters, '====filters====')
	conditions = ""

	if filters.get('id'):
		conditions += " and ss.name = '{0}'".format(filters.get('id'))
	
	if filters.get('is_active'):
		conditions += " and ss.is_active = '{0}'".format(filters.get('is_active'))

	return conditions

def get_data(filters, earnings, deduction):
	conditions = get_conditions(filters)
	data = []

	data = frappe.db.sql("""
			SELECT ss.name as id, ss.is_active,
				ss.custom_employee_no as employee_no,
				ss.custom_employee_name as employee_name,
				emp.custom_idresidency_number as iD_residency_number
			From `tabSalary Structure` as ss
			LEFT OUTER JOIN `tabEmployee` as emp ON emp.name = ss.custom_employee_no
			WHERE ss.docstatus = 1 {0}
		""".format(conditions), filters, as_dict=1, debug=1)
	
	for row in data:
		components = frappe.db.sql("""
			SELECT tsd.salary_component, tsd.amount 
			From `tabSalary Detail` tsd 
			WHERE tsd.docstatus = 1 and tsd.parent = '{0}'
			""".format(row.id), as_dict=1, debug=1)
		
		total_earnings = 0
		total_deduction = 0
		for com in components:
			for ear in earnings:
				if com.salary_component == ear:
					total_earnings = total_earnings + com['amount']
					row.update({_(ear): com['amount']})

			for ded in deduction:
				if com.salary_component == ded:
					total_deduction = total_deduction + com['amount']
					row.update({_(ded): com['amount']})

		row.update({_('total_earnings'): total_earnings})
		row.update({_('total_deduction'):total_deduction})
		row.update({_('net_amount'): total_earnings})
	
	return data
