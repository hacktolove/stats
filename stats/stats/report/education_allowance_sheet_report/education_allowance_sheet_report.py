# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _ 

def execute(filters=None):
	if not filters: filters = {}

	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)

	if not data:
		frappe.msgprint(_("No records found"))
		return columns, data

	return columns, data

def get_columns():
	columns = [
		{
			"fieldname" : 'emp_no',
			"fieldtype" : 'Link',
			"label" : _('Employee No'),
			"options"  : 'Employee',
			"width" : 150
		},
		{
			"fieldname" : 'emp_name',
			"fieldtype" : 'Data',
			"label" : _('Employee Name'),
			"width" : 250
		},
		{
			"fieldname" : 'idresidency_no',
			"fieldtype" : 'Data',
			"label" : _('ID/Residency No'),
			"width" : 130
		},
		{
			"fieldname" : 'sub_department',
			"fieldtype" : 'Link',
			"label" : _('Sub Department'),
			"options" : 'Department',
			"width" : 220
		},
		{
			"fieldname" : 'grade',
			"fieldtype" : 'Link',
			"label" : _('Grade'),
			"options" : 'Employee Grade',
			"width" : 100
		},
		{
			"fieldname" : 'season',
			"fieldtype" : 'Link',
			"label" : _('Season'),
			"options" : 'Season ST',
			"width" : 130
		},
		{
			"fieldname" : 'no_of_kids',
			"fieldtype" : 'Int',
			"label" : _('No of Kids'),
			"width" : 100
		},
		{
			"fieldname" : 'total_due_amount',
			"fieldtype" : 'Currency',
			"label" : _('Total Due Amount'),
			"width" : 130
		},
	]
	return columns

def get_conditions(filters):
	condition = ""
	if filters.get('emp_no'):
		condition += 'AND tead.employee_no = "{0}"'.format(filters.get('emp_no'))

	if filters.get('sub_department'):
		condition += 'AND tead.sub_department = "{0}"'.format(filters.get('sub_department'))

	return condition

def get_data(filters):
	condition = get_conditions(filters)
	data = frappe.db.sql(
		'''
			SELECT 
				tead.employee_no as "emp_no", 
				tead.employee_name as "emp_name",  
				e.custom_idresidency_number as "idresidency_no", 
				tead.sub_department as "sub_department", 
				tead.grade as "grade", 
				tard.season as "season", 
				COUNT(DISTINCT tard.child_name) as "no_of_kids", 
				SUM(DISTINCT tead.approved_amount) as "total_due_amount"
			FROM 
				`tabEducation Allowance Sheet ST` tea
			INNER JOIN  
				`tabEducation Allowance Sheet Details ST` tead  
			ON 
				tead.parent = tea.name
			LEFT OUTER JOIN 
				`tabEducation Allowance Request Details ST` tard
			ON 
				tard.parent = tead.education_allowance_request_reference
			INNER JOIN 
				`tabEmployee` e
			ON 
				tead.employee_no = e.name
			WHERE 
				tea.docstatus != 2 {0}
			GROUP BY 
				tead.employee_no
		'''.format(condition), as_dict = 1
	)
	return data