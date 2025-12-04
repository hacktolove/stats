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
			'fieldname' : 'pr_date',
			'fieldtype' : 'Date',
			'label' : _('PR Date'),
			'width' : 120,
		},
		{
			'fieldname' : 'employee',
			'fieldtype' : 'Link',
			'label' : _('Employee'),
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
			'fieldname' : 'email',
			'fieldtype' : 'Data',
			'label' : _('Email'),
			'width' : 180,
		},
		{
			'fieldname' : 'phone',
			'fieldtype' : 'Data',
			'label' : _('Phone'),
			'width' : 140,
		},
		{
			'fieldname' : 'post_type',
			'fieldtype' : 'Link',
			'label' : _('Post Type'),
			'width' : 130,
			'options' : 'Post Type ST'
		},
		{
			'fieldname' : 'address',
			'fieldtype' : 'Data',
			'label' : _('Address'),
			'width' : 200,
		},
		{
			'fieldname' : 'number_of_attendees',
			'fieldtype' : 'Data',
			'label' : _('Number of Attendees'),
			'width' : 120,
		},
		{
			'fieldname' : 'goals',
			'fieldtype' : 'Data',
			'label' : _('Goals'),
			'width' : 120,
		},
		{
			'fieldname' : 'next_steps',
			'fieldtype' : 'Data',
			'label' : _('Next Steps'),
			'width' : 120,
		},
		{
			'fieldname': 'required_service',
			'fieldtype': 'Link',
			'label': _('Required Service'),
			'options': 'Required Service ST',
			'width' : 120,
		},
		{
			'fieldname': 'request_date',
			'fieldtype': 'Date',
			'label': _('Request Date'),
			'width' : 120,
		},
		{
			'fieldname': 'request_time',
			'fieldtype': 'Data',
			'label': _('Request Time'),
			'width' : 120,
		},
	]
	return columns

def get_conditions(filters):
	condiitons = " "

	if filters.get('pr_date'):
		condiitons += " AND tprs.pr_date = '{0}'".format(filters.get('pr_date'))
	
	if filters.get('request_date'):
		condiitons += " AND tprs.request_date  = '{0}'".format(filters.get('request_date'))

	if filters.get('employee'):
		condiitons += " AND tprs.employee  = '{0}'".format(filters.get('employee'))
	
	if filters.get('main_department'):
		condiitons += " AND tprs.main_department  = '{0}'".format(filters.get('main_department'))

	if filters.get('sub_department'):
		condiitons += " AND tprs.sub_department  = '{0}'".format(filters.get('sub_department'))

	if filters.get('post_type'):
		condiitons += " AND tprs.post_type = '{0}'".format(filters.get('post_type'))

	return condiitons

def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		'''
		SELECT 
			tprs.pr_date,
			tprs.employee,
			tprs.employee_name,
			tprs.main_department,
			tprs.sub_department,
			tprs.email,
			tprs.phone,
			tprs.post_type,
			tprs.address,
			tprs.number_of_attendees,
			tprs.goals,
			tprs.next_steps,
			tprs.required_service,
			tprs.request_date,
			tprs.request_time
		FROM 
			`tabPost Request ST` tprs
		WHERE 
			tprs.docstatus != 2 
			{0};
		'''.format(conditions),
	as_dict=1)

	print(data)

	return data
