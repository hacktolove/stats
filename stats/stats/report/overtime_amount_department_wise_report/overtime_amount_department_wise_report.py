# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
def execute(filters=None):
	if not filters:
		filters = {}
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{
			'fieldname' : 'department',
			'fieldtype' : 'Link',
			'label' : _('Department Name'),
			'options' : 'Department',
			'width' : 200
		},
		{
			'fieldname' : 'amount',
			'fieldtype' : 'Currency',
			'label' : _('Amount'),
			'width' : 150
		}
	]
	return columns

def get_conditions(filters):
	conditions = {}
	for key,value in filters.items():
		if filters.get(key):
			conditions[key] = value
	return conditions

def get_data(filters):
	conditions = get_conditions(filters)
	data = []

	if conditions.get('based_on') == 'Main Department':
		overtime_data = frappe.db.sql(
			'''
				SELECT  
					tors.main_department as "department",
					SUM(tors.total_due_amount) as "total" 	
				FROM 
					`tabOvertime Request ST` tors 
				WHERE 
					tors.docstatus = 1
				AND
					tors.creation_date BETWEEN '{0}' AND '{1}'	
				GROUP BY 
					tors.main_department;
			'''.format(conditions.get('from_date'), conditions.get('to_date')), as_dict = 1
		)
	elif conditions.get('based_on') == 'Sub Department':
		overtime_data = frappe.db.sql(
			'''
				SELECT  
					tors.sub_department as "department",
					SUM(tors.total_due_amount) as "total" 	
				FROM 
					`tabOvertime Request ST` tors 
				WHERE 
					tors.docstatus = 1
				AND
					tors.creation_date BETWEEN '{0}' AND '{1}'
				GROUP BY 
					tors.sub_department; 
			'''.format(conditions.get('from_date'), conditions.get('to_date')), as_dict = 1
		)

	for od in overtime_data:
		row = frappe._dict({
			'department' : od['department'],
			'amount' : od['total']
		})
		data.append(row)
	return data