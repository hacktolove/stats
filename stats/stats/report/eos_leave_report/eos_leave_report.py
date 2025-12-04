# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate
from erpnext.accounts.utils import get_fiscal_year

def execute(filters=None):
	if not filters: filters = {}
	columns, data = [], []

	columns = get_columns()
	data = get_data(filters)
	
	return columns, data


def get_columns():
	columns = [
		dict(
			fieldname = 'employee',
			fieldtype = 'Link',
			label = _('Employee'),
			options = 'Employee',
			width = 150,
		),
		dict(
			fieldname = 'employee_name',
			fieldtype = 'Data',
			label = _('Employee Name'),
			width = 150,
		),
		dict(
			fieldname = 'main_department',
			fieldtype = 'Link',
			label = _('Main Department'),
			options = 'Department',
			width = 150,
		),
		dict(
			fieldname = 'sub_department',
			fieldtype = 'Link',
			label = _('Sub Department'),
			options = 'Department',
			width = 150,
		),
		dict(
			fieldname = 'idresidency_number',
			fieldtype = 'Data',
			label = _('ID/Residency'),
			width = 150,
		),
		dict(
			fieldname = 'joining_date',
			fieldtype = 'Date',
			label = _('Joining Date'),
			width = 150,
		),
		dict(
			fieldname = 'last_working_date',
			fieldtype = 'Date',
			label = _('Last Working Date'),
			width = 150,
		),
		dict(
			fieldname = 'leave_type',
			fieldtype = 'Link',
			label = _('Leave Type'),
			options = 'Leave Type',
			width = 200,
		),
		dict(
			fieldname = 'consumed',
			fieldtype = 'Data',
			label = _('Consumed'),
			width = 130,
		),
		dict(
			fieldname = 'balance',
			fieldtype = 'Data',
			label = _('Balance'),
			width = 130,
		)
	]
	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get('employee'):
		conditions += "AND er.employee_no = '{0}'".format(filters.get('employee'))

	if filters.get('main_department'):
		conditions += "AND er.main_department = '{0}'".format(filters.get('main_department'))

	if filters.get('sub_department'):
		conditions += "AND er.sub_department = '{0}'".format(filters.get('sub_department'))

	return conditions

def get_data(filters):
	condition = get_conditions(filters)
	data = []
	query_data = frappe.db.sql(
		'''
			SELECT 
				er.employee_no,
				er.employee_name,
				er.main_department,
				er.sub_department,
				e.custom_idresidency_number,
				e.date_of_joining,
				er.last_working_days,
				e.custom_contract_type
			FROM 
				`tabEmployee Resignation ST` er
			INNER JOIN
				`tabEmployee` e 	
			ON 
				er.employee_no = e.name
			WHERE
				er.docstatus != 2 {0};
		'''.format(condition)
	,as_dict = 1
	)
	
	if len(query_data) > 0:
		for d in query_data:
			# Leave Type Or Annual Leave
			default_annual_leave = frappe.db.get_value("Contract Type ST", d['custom_contract_type'], 'annual_leave_type')

			# Consumed Balance From Joining
			consumed_leaves = frappe.db.sql('''
				SELECT 
					SUM(tla.total_leave_days) as "total_leaves"
				FROM 
					`tabLeave Application` tla 
				WHERE 
					tla.employee = '{0}'
				AND tla.leave_type = '{1}' AND tla.docstatus = 1 AND tla.status = 'Approved';
			'''.format(d['employee_no'], default_annual_leave), as_dict = 1)
			total_consumed_leaves = 0
			if len(consumed_leaves) > 0:
				if consumed_leaves[0].total_leaves != None:
					total_consumed_leaves = consumed_leaves[0].total_leaves

			# Current Fiscal Year Start And End Date
			current_fiscal_year = get_fiscal_year(nowdate(), as_dict=True)
			fiscal_year_start_date = current_fiscal_year.year_start_date
			fiscal_year_end_date = current_fiscal_year.year_end_date
			
			# Allocated And Used Leaves Calculation For Balance
			allocated_leaves = frappe.db.sql('''
				SELECT tla.total_leaves_allocated as "allocated"
				FROM `tabLeave Allocation` tla 
				WHERE tla.leave_type = '{0}' AND tla.employee = '{1}' AND  tla.from_date >= '{2}' AND tla.to_date <= '{3}'
			'''.format(default_annual_leave, d['employee_no'], fiscal_year_start_date, fiscal_year_end_date), as_dict = 1)

			allocated = 0
			if len(allocated_leaves) > 0:
				if allocated_leaves[0].allocated != None:
					allocated = allocated_leaves[0].allocated

			used_leaves = frappe.db.sql('''
				SELECT SUM(tla.total_leave_days) as "used"
				FROM `tabLeave Application` tla 
				WHERE tla.leave_type = '{0}' AND tla.employee = '{1}' AND  tla.from_date >= '{2}' AND tla.to_date <= '{3}' AND tla.docstatus = 1;
			'''.format(default_annual_leave, d['employee_no'], fiscal_year_start_date, fiscal_year_end_date), as_dict = 1)
		
			used = 0
			if len(used_leaves) > 0:
				if used_leaves[0].used != None:
					used = used_leaves[0].used

			balance_remaining = allocated - used
			row = frappe._dict({
				'employee' : d['employee_no'],
				'employee_name' : d['employee_name'],
				'main_department' : d['main_department'],
				'sub_department' : d['sub_department'],
				'idresidency_number' : d['custom_idresidency_number'],
				'joining_date' : d['date_of_joining'],
				'last_working_date' : d['last_working_days'],
				'leave_type' : default_annual_leave,
				'consumed' : total_consumed_leaves,
				'balance' : round(balance_remaining, 2)
			}) 
			data.append(row)

	if filters.get('leave_type'):
		fdata = []
		for d in data:
			if d['leave_type'] == filters.get('leave_type'):
				fdata.append(d)
		return fdata
	
	return data

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_leave_type_list(doctype, txt, searchfield, start, page_len, filters):
	data = frappe.db.sql('''
		SELECT DISTINCT(tcts.annual_leave_type)
		FROM `tabContract Type ST` tcts
		WHERE  tcts.annual_leave_type IS NOT NULL AND tcts.annual_leave_type like %(txt)s;
	''', {"txt": "%%%s%%" % txt})

	return data