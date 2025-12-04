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
			'fieldname' : 'pr_name',
			'fieldtype' : 'Link',
			'label' : _('Payment Request Ref'),
			'options': 'Payment Request ST',
			'width' : 130
		}, 
		{
			'fieldname' : 'pr_date',
			'fieldtype' : 'Date',
			'label' : _('Payment Request Date'),
			'width' : 130
		}, 
		{
			'fieldname' : 'ref_name',
			'fieldtype' : 'Data',
			'label' : _('Reference Name'),
			'width' : 130
		}, 
		{
			'fieldname' : 'ref_date',
			'fieldtype' : 'Date',
			'label' : _('Reference Date'),
			'width' : 130
		}, 
		{
			'fieldname' : 'pr_workflow_status',
			'fieldtype' : 'Data',
			'label' : _('PR Workflow Status'),
			'width' : 130
		}, 
		{
			'fieldname' : 'pp_name',
			'fieldtype' : 'Link',
			'label' : _('Payment Procedure Ref'),
			'options': 'Payment Procedure ST',
			'width' : 130
		}, 
		{
			'fieldname' : 'pp_workflow_status',
			'fieldtype' : 'Data',
			'label' : _('PP Workflow Status'),
			'width' : 130
		}, 
		{
			'fieldname' : 'no_of_employee',
			'fieldtype' : 'Int',
			'label' : _('No Of Employee'),
			'width' : 130
		},
		{
			'fieldname' : 'total_amount',
			'fieldtype' : 'Currency',
			'label' : _('Total Amount'),
			'width' : 130
		}, 
		{
			'fieldname' : 'payment_status',
			'fieldtype' : 'Data',
			'label' : _('Payment Status'),
			'width' : 130
		},
	]
	return columns

def get_conditions(filters):
	conditions = ""
	if filters != {}:
		if filters.get('reference'):
			conditions += 'AND tprs.reference_name = "{0}"'.format(filters.get('reference'))
	return conditions

def get_data(filters):
	conditions = get_conditions(filters)
	data = []

	pr_data = frappe.db.sql(
		'''
		SELECT 
			tprs.name as "pr_name",
			tprs.creation, 
			tprs.reference_name,
			tprs.reference_no, 
			tprs.workflow_state,  
			tpps.name,
			IFNULL(tpps.name, "Not Created") as "pp_name",
			IFNULL(COUNT(tedfps.name),0) as "no_of_emp" ,
			tprs.total_amount,
			IFNULL(IF(tpps.docstatus = 1, 'Done', 'Pending'),"Not Created")   as 'payment_status'		
		FROM 
			`tabPayment Request ST` tprs
		LEFT JOIN 
			`tabEmployee Details For Payment ST` tedfps
		ON
			tedfps.parent=tprs.name
		LEFT JOIN 
			`tabPayment Procedure ST` tpps 
		ON 
			tprs.name = tpps.payment_request_reference
		WHERE 
			tprs.docstatus = 1
		AND 
			tprs.reference_name IN ('Overtime Sheet ST', 'Business Trip Sheet ST', 'End Of Service Sheet ST', 'Employee Reallocation Sheet ST', 'Education Allowance Sheet ST')	
		AND 
			tprs.transaction_date BETWEEN '{0}' AND '{1}'
		{2}
		GROUP BY tedfps.parent
		'''.format(filters.get('from_date'), filters.get('to_date'), conditions) 
		,as_dict = 1
	)

	if len(pr_data) > 0:
		for pr in pr_data:
			ref_name = pr['reference_name']
			
			if ref_name in ['End Of Service Sheet ST', 'Employee Reallocation Sheet ST']:
				ref_date = frappe.db.get_value(ref_name, pr['reference_no'], 'transaction_date')
			elif ref_name in ['Overtime Sheet ST', 'Education Allowance Sheet ST']:
				ref_date = frappe.db.get_value(ref_name, pr['reference_no'], 'creation_date')
			elif ref_name in ['Business Trip Sheet ST']:
				ref_date = frappe.db.get_value(ref_name, pr['reference_no'], 'date')

			row = frappe._dict({
				'pr_name' : pr['pr_name'],
				'pr_date' : pr['creation'],
				'ref_name': pr['reference_name'],
				'ref_date': ref_date,
				'pr_workflow_status' : pr['workflow_state'],
				'pp_name' : pr['pp_name'],
				'pp_workflow_status' : '',
				'no_of_employee' : pr['no_of_emp'],
				'total_amount' : pr['total_amount'],
				'payment_status' : pr['payment_status']
			})
			data.append(row)

	return data