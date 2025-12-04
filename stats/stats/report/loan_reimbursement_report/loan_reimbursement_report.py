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
			'fieldname' : 'id',
			'fieldtype' : 'Link',
			'label' : _('ID'),
			'options' : 'Loan Reimbursement ST',
			'width' : 150
		},
		{
			'fieldname' : 'workflow_status',
			'fieldtype' : 'Data',
			'label' : _('Workflow Status'),
			'width' : 150
		},
		{
			'fieldname' : 'status',
			'fieldtype' : 'Data',
			'label' : _('Status'),
			'width' : 150
		},
		{
			'fieldname' : 'employee_no',
			'fieldtype' : 'Link',
			'label' : _('Employee No'),
			'options' : 'Employee',
			'width' : 150
		},
		{
			'fieldname' : 'employee_name',
			'fieldtype' : 'Data',
			'label' : _('Employee Name'),
			'width' : 150
		},
		{
			'fieldname' : 'employee_number',
			'fieldtype' : 'Data',
			'label' : _('Employee Number'),
			'width' : 150
		},
		{
			'fieldname' : 'id_residency_number',
			'fieldtype' : 'Data',
			'label' : _('ID/Residency Number'),
			'width' : 150
		},
		{
			'fieldname' : 'main_department',
			'fieldtype' : 'Link',
			'label' : _('Main Department'),
			'options' : 'Department',
			'width' : 150
		},
		{
			'fieldname' : 'sub_department',
			'fieldtype' : 'Link',
			'label' : _('Sub Department'),
			'options' : 'Department',
			'width' : 150
		},
		{
			'fieldname' : 'deduction_start_date',
			'fieldtype' : 'Date',
			'label' : _('Deduction Start Date'),
			'width' : 150
		},
		{
			'fieldname' : 'decision_number',
			'fieldtype' : 'Data',
			'label' : _('Decision Number'),
			'width' : 150
		},
		{
			'fieldname' : 'bank_loan_reference',
			'fieldtype' : 'Data',
			'label' : _('Bank Loan Reference'),
			'width' : 150
		},
		{
			'fieldname' : 'decision_date',
			'fieldtype' : 'Date',
			'label' : _('Decision Date'),
			'width' : 150
		},
		{
			'fieldname' : 'total_amount',
			'fieldtype' : 'Currency',
			'label' : _('Total Amount'),
			'width' : 150
		},
		{
			'fieldname' : 'instalment_value',
			'fieldtype' : 'Currency',
			'label' : _('Installment Value'),
			'width' : 150
		},
		{
			'fieldname' : 'last_instalment',
			'fieldtype' : 'Currency',
			'label' : _('Last Installment'),
			'width' : 150
		},
		{
			'fieldname' : 'instalment_done',
			'fieldtype' : 'Int',
			'label' : _('Installment Done'),
			'width' : 150
		},
		{
			'fieldname' : 'installment_pending',
			'fieldtype' : 'Int',
			'label' : _('Installment Pending'),
			'width' : 150
		},
	]
	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("employee"):
		conditions += " AND tlrs.employee_no = '{0}'".format(filters.get("employee"))

	if filters.get("main_department"):
		conditions += " AND tlrs.main_department = '{0}'".format(filters.get("main_department"))

	if filters.get("sub_department"):
		conditions += " AND tlrs.sub_department = '{0}'".format(filters.get("sub_department"))
	
	if filters.get("decision_number"):
		conditions += " AND tlrs.decision_number LIKE '%{0}%'".format(filters.get("decision_number"))

	if filters.get("bank_loan_reference"):
		conditions += " AND tlrs.bank_loan_reference LIKE '%{0}%'".format(filters.get("bank_loan_reference"))

	return conditions

def get_data(filters):
	conditions = get_conditions(filters)
	data = []
	query_data = frappe.db.sql(
	'''
	SELECT 
		tlrs.name, 
		tlrs.workflow_state,
		tlrs.employee_no,
		tlrs.employee_name,
		tlrs.main_department,
		tlrs.sub_department,
		tlrs.decision_number,
		tlrs.decision_date,
		tlrs.bank_loan_reference,
		tlrs.deduction_start_date,
		tlrs.status,
		tlrs.total_amount,
		tlrs.instalment_value,
		tlrs.last_instalment,
		SUM(CASE WHEN discount.status='Scheduled' THEN 1 ELSE 0 END) AS 'instalment_pending',
		SUM(CASE WHEN discount.status IN ('Deducted','Early-Payment') THEN 1 ELSE 0 END) AS 'instalment_done',
		te.employee_number,
		te.custom_idresidency_number
	FROM `tabTable Of Discounts ST` discount
	RIGHT OUTER JOIN  `tabLoan Reimbursement ST` tlrs
	INNER JOIN `tabEmployee` te 
	ON te.name = tlrs.employee_no
	ON discount.parent  = tlrs.name
	WHERE tlrs.docstatus != 2 {0}
	GROUP BY tlrs.name
	ORDER BY tlrs.name;
	'''.format(conditions)
	, as_dict = 1)

	for d in query_data:
		row = frappe._dict({
			'id' : d['name'],
			'workflow_status' : d['workflow_state'],
			'status' : d['status'],
			'employee_no' : d['employee_no'],
			'employee_name' : d['employee_name'],
			'employee_number' : d['employee_number'],
			'id_residency_number' : d['custom_idresidency_number'],
			'main_department' : d['main_department'],
			'sub_department' : d['sub_department'],
			'deduction_start_date' : d['deduction_start_date'],
			'decision_number' : d['decision_number'],
			'bank_loan_reference' : d['bank_loan_reference'],
			'decision_date' : d['decision_date'],
			'total_amount' : d['total_amount'],
			'instalment_value' : d['instalment_value'],
			'last_instalment' : d['last_instalment'],
			'instalment_done' : d['instalment_done'], 
			'installment_pending' : d['instalment_pending'],
		})
		data.append(row)

	return data