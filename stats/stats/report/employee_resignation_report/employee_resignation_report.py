# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters: filters = {}
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	columns = [
		{
			'fieldname' : 'resignation_date',
			'fieldtype' : 'Date',
			'label' : _('Resignation Date'),
			'width' : 150
		},
		{
			'fieldname' : 'employee_no',
			'fieldtype' : 'Link',
			'label' : _('Employee No'),
			'width' : 140,
			'options' : 'Employee'
		},
		{
			'fieldname' : 'employee_name',
			'fieldtype' : 'Data',
			'label' : _('Employee Name'),
			'width' : 250,
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
		{
			'fieldname': 'section',
			'fieldtype': 'Link',
			'label': _('Section'),
			'options': 'Section ST',
			'width' : 150,
		},
		{
			'fieldname': 'branch',
			'fieldtype': 'Link',
			'label': _('Branch'),
			'options': 'Branch',
			'width' : 150,
		},
		{
			'fieldname': 'resignation_type',
			'fieldtype': 'Link',
			'label': _('Resignation Type'),
			'options': 'Resignation Type ST',
			'width' : 150,
		},
		{
			'fieldname' : 'last_working_days',
			'fieldtype' : 'Date',
			'label' : _('Last Working Date'),
			'width' : 150
		},
		{
			'fieldname' : 'employee_evacuation_status',
			'fieldtype' : 'Data',
			'label' : _('Employee Evacuation Status'),
			'width' : 150
		},
		{
			'fieldname' : 'exit_interview_status',
			'fieldtype' : 'Data',
			'label' : _('Exit Interview Status'),
			'width' : 150
		},
		{
			'fieldname' : 'end_of_service_calculation_status',
			'fieldtype' : 'Data',
			'label' : _('End Of Service Calculation Status'),
			'width' : 150
		},
	]
	return columns


def get_conditions(filters):
	conditions = ""
	if filters.get('resignation_date'):
		conditions += " AND ters.resignation_date = '{0}'".format(filters.get('resignation_date'))
	
	if filters.get('section'):
		conditions += " AND ters.`section`  = '{0}'".format(filters.get('section'))

	if filters.get('employee_no'):
		conditions += " AND ters.employee_no = '{0}'".format(filters.get('employee_no'))
	
	if filters.get('main_department'):
		conditions += " AND ters.main_department  = '{0}'".format(filters.get('main_department'))

	if filters.get('sub_department'):
		conditions += " AND ters.sub_department  = '{0}'".format(filters.get('sub_department'))

	if filters.get('branch'):
		conditions += " AND ters.branch = '{0}'".format(filters.get('branch'))

	return conditions

def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		'''
			SELECT 
				ters.resignation_date ,
				ters.employee_no,
				ters.employee_name,
				ters.main_department,
				ters.sub_department,
				ters.`section`,
				ters.branch,
				ters.resignation_type,
				ters.last_working_days,
				ters.employee_evacuation_status,
				ters.exit_interview_status,
				ters.end_of_service_calculation_status 
			FROM 
				`tabEmployee Resignation ST` ters 
			WHERE 
				ters.docstatus != 2
				{0};
		'''.format(conditions),
		as_dict = 1)

	return data
