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
			'fieldname' : 'employee_no',
			'fieldtype' : 'Link',
			'label' : _('Employee'),
			'width' : 150,
			'options' : 'Employee'
		},
		{
			'fieldname' : 'employee_name',
			'fieldtype' : 'Data',
			'label' : _('Employee Name'),
			'width' : 150,
		},
		{
			'fieldname' : 'request_ref',
			'fieldtype' : 'Link',
			'label' : _('Request Ref'),
			'width' : 150,
			'options' : 'Overtime Request ST'
		},
		{
			'fieldname' : 'date',
			'fieldtype' : 'Date',
			'label' : _('Date'),
			'width' : 150,
		},
		{
			'fieldname' : 'no_of_days',
			'fieldtype' : 'Float',
			'label' : _('No of Days'),
			'width' : 150,
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
			'fieldname' : 'approved_days',
			'fieldtype' : 'Float',
			'label' : _('Approved Days'),
			'width' : 150,
		},
		{
			'fieldname' : 'total_no_of_hours',
			'fieldtype' : 'Float',
			'label' : _('Total No Of Hours'),
			'width' : 150,
		},
		{
			'fieldname' : 'amount',
			'fieldtype' : 'Currency',
			'label' : _('Amount'),
			'width' : 150,
		},
		{
			'fieldname' : 'status',
			'fieldtype' : 'Data',
			'label' : _('Status'),
			'width' : 150,
		},
		{
			'fieldname': 'main_department',
			'fieldtype': 'Link',
			'label': _('Main Department'),
			'options': 'Department',
			'width' : 150,
		},
		{
			'fieldname': 'sub_department',
			'fieldtype': 'Link',
			'label': _('Sub Department'),
			'options': 'Department',
			'width' : 150,
		},
	]
	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get('main_department'):
		conditions += 'AND tors.main_department = "{0}"'.format(filters.get('main_department'))

	if filters.get('sub_department'):
		conditions += 'AND tors.sub_department = "{0}"'.format(filters.get('sub_department'))

	if filters.get('employee'):
		conditions += 'AND teords.employee_no = "{0}"'.format(filters.get('employee'))

	if filters.get('status'):
		conditions += 'AND teords.request_status = "{0}"'.format(filters.get('status'))
	return conditions

def get_data(filters):
	conditions = get_conditions(filters)
	data = []

	overtime_data = frappe.db.sql('''
		SELECT 
			teords.employee_no,
			teords.employee_name,
			tors.name,
			tors.creation_date,
			tors.total_no_of_days,
			(teords.total_no_of_days * teords.no_of_hours_per_day) as 'total_no_of_hours',
			teords.due_amount,
			teords.request_status,
			tors.main_department,
			tors.sub_department,
			toaeds.no_of_vacation,
			toaeds.no_of_absent,
			toaeds.approved_days
		FROM 
			`tabOvertime Request ST` tors 
		INNER JOIN 
			`tabEmployee Overtime Request Details ST` teords 
		ON 
			tors.name = teords.parent
		INNER JOIN 
			`tabOvertime Approval Request ST` toars
		ON 
			toars.overtime_reference = tors.name
		INNER JOIN 
			`tabOvertime Approval Employee Details ST` toaeds
		ON 
			toaeds.parent = toars.name
		WHERE
			tors.creation_date BETWEEN '{0}' and '{1}'
			{2}
		ORDER BY
			teords.employee_no;
	'''.format(filters.get('from_date'), filters.get('to_date'), conditions),debug=1,
	as_dict = 1)

	if len(overtime_data) > 0:
		for od in overtime_data:
			row = frappe._dict({
				'employee_no' : od['employee_no'],
				'employee_name' : od['employee_name'],
				'request_ref' : od['name'],
				'date' : od['creation_date'],
				'no_of_days' : od['total_no_of_days'],
				'total_no_of_hours' : od['total_no_of_hours'],
				'amount' : od['due_amount'],
				'status' : od['request_status'],
				'main_department' : od['main_department'],
				'sub_department' : od['sub_department'],
				'no_of_vacation' : od['no_of_vacation'],
				'no_of_absent' : od['no_of_absent'],
				'approved_days' : od['approved_days']
			})
			data.append(row)
	return data