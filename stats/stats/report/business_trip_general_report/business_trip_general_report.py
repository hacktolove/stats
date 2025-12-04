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
			'fieldname' : 'business_trip_req_ref',
			'fieldtype' : 'Link',
			'label' : _('Business Trip Req Ref'),
			'options': 'Business Trip Request ST',
			'width' : 150
		},
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
			'fieldname': 'main_department',
			'fieldtype': 'Link',
			'label': _('Main Department'),
			'options': 'Department',
			'width' : 200,
		},
		{
			'fieldname': 'sub_department',
			'fieldtype': 'Link',
			'label': _('Sub Department'),
			'options': 'Department',
			'width' : 200,
		},
		{
			'fieldname' : 'total_no_of_days',
			'fieldtype' : 'Float',
			'label' : _('Total No of Days'),
			'width' : 150,
		},
		{
			'fieldname' : 'trip_classification',
			'fieldtype' : 'Data',
			'label' : _('Trip Classification'),
			'width' : 150,
		},
		{
			'fieldname' : 'place_of_visit',
			'fieldtype' : 'Data',
			'label' : _('Place Of Visit'),
			'width' : 150,
		},
		{
			'fieldname' : 'due_amount',
			'fieldtype' : 'Currency',
			'label' : _('Due Amount'),
			'width' : 150,
		},
		{
			'fieldname' : 'status',
			'fieldtype' : 'Data',
			'label' : _('Status'),
			'width' : 150,
		},
		{
			'fieldname' : 'start_date',
			'fieldtype' : 'Date',
			'label' : _('Business Trip Start Date'),
			'width' : 150,
		},
		{
			'fieldname' : 'end_date',
			'fieldtype' : 'Date',
			'label' : _('Business Trip End Date'),
			'width' : 150,
		},
	]
	return columns

def get_conditions(filters):
	if filters != {}:
		conditions = ""

		if filters.get('main_department'):
			conditions += 'AND tbtrs.main_department = "{0}"'.format(filters.get('main_department'))
		
		if filters.get('sub_department'):
			conditions += 'AND tbtrs.sub_department = "{0}"'.format(filters.get('sub_department'))

		if filters.get('employee'):
			conditions += 'AND tbtrs.employee_no = "{0}"'.format(filters.get('employee'))

		if filters.get('status'):
			conditions += 'AND tbtrs.status = "{0}"'.format(filters.get('status'))

		if filters.get('trip_classification'):
			conditions += 'AND tbtrs.trip_classification = "{0}"'.format(filters.get('trip_classification'))
	
	return conditions

def get_data(filters):
	conditions = get_conditions(filters)
	data = []

	trip_data = frappe.db.sql(
		'''
		SELECT 
			tbtrs.name as business_trip_req_ref,
			tbtrs.employee_no,
			tbtrs.employee_name,
			tbtrs.main_department,
			tbtrs.sub_department,
			tbtrs.total_no_of_days,
			tbtrs.trip_classification,
			IF(tbtrs.trip_classification = 'Internal', tbtrs.saudi_city , tbtrs.country) as place_of_visit,
			tbtrs.grade,
			tbtrs.status,
			tbtrs.per_diem_amount as due_amount,
			tbtrs.business_trip_start_date as start_date,
			tbtrs.business_trip_end_date as end_date
		FROM 
			`tabBusiness Trip Request ST` tbtrs 
		WHERE
			tbtrs.creation_date BETWEEN "{0}" AND "{1}"
			{2}
		'''.format(filters.get('from_date'), filters.get('to_date'), conditions)
		,as_dict = 1
	)

	return trip_data