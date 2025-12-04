# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import nowdate

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
			'width' : 250,
		},
		{
			'fieldname': 'main_department',
			'fieldtype': 'Link',
			'label': _('Main Department'),
			'options': 'Department',
			'width' : 250,
		},
		{
			'fieldname': 'sub_department',
			'fieldtype': 'Link',
			'label': _('Sub Department'),
			'options': 'Department',
			'width' : 250,
		},
		{
			'fieldname' : 'balance',
			'fieldtype' : 'Float',
			'label' : _('Balance'),
			'width' : 150
		},
		{
            'fieldname' : 'total_no_of_req',
            'fieldtype' : 'Float',
            'label' : _('Total No Of Request'),
            'width' : 130
        }		
	]
	return columns

def get_conditions(filters):
	# current_fiscal_year = get_fiscal_year(nowdate(), as_dict=True)
	# print(current_fiscal_year)
	if filters != {}:
		conditions = "WHERE "
		# conditions = ''
		# conditions += 'and tbtrs.business_trip_start_date between "{0}" and "{1}"'.format(current_fiscal_year.year_start_date, current_fiscal_year.year_end_date)
		if filters.get('main_department'):
			conditions += 'te.department = "{0}"'.format(filters.get('main_department')) if len(conditions) == 6 else 'AND te.department = "{0}"'.format(filters.get('main_department'))
		
		if filters.get('sub_department'):
			conditions += 'te.custom_sub_department = "{0}"'.format(filters.get('sub_department')) if len(conditions) == 6 else 'AND te.custom_sub_department = "{0}"'.format(filters.get('sub_department'))

		if filters.get('employee'):
			conditions += 'te.name = "{0}"'.format(filters.get('employee')) if len(conditions) == 6 else 'AND te.name = "{0}"'.format(filters.get('employee'))

		return conditions

def get_data(filters):
	conditions = get_conditions(filters)
	data = []
	
	emp_balance_data = frappe.db.sql(
		'''
		SELECT 
			te.name, 
			te.employee_name,
			te.department,
			te.custom_sub_department,
			te.custom_no_of_business_trip_days_remaining
		FROM 
			`tabEmployee` te  	
		{0}
		'''.format(conditions if conditions != None else ''),
		as_dict = 1,debug = 1
	)

	for emp in emp_balance_data:
		no_of_request = frappe.db.sql('''
			SELECT 
				tbtrs.employee_no, COUNT(tbtrs.name) as count
			FROM 
				`tabBusiness Trip Request ST` tbtrs 
			WHERE 
				tbtrs.employee_no = "{0}" AND tbtrs.docstatus  = 1 AND tbtrs.status = "Approved"
		'''.format(emp['name']) ,as_dict = 1)

		if len(no_of_request) > 0:
			emp['total_no_of_req'] = no_of_request[0].count
		
	if len(emp_balance_data) > 0:
		for emp in emp_balance_data:
			row = frappe._dict({
				'employee_no' : emp['name'],
				'employee_name' : emp['employee_name'],
				'main_department' : emp['department'],
				'sub_department' : emp['custom_sub_department'],	
				'balance' : emp['custom_no_of_business_trip_days_remaining'],
				'total_no_of_req' : emp['total_no_of_req']
			})

			data.append(row)

	return data