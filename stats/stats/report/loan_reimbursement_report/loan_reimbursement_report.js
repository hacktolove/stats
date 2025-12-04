// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Loan Reimbursement Report"] = {
	"filters": [
		{
			fieldname : 'employee',
			fieldtype : 'Link',
			label : __('Employee'),
			options : 'Employee'
		},
		{
			fieldname : 'main_department',
			fieldtype : 'Link',
			label : __('Main Department'),
			options : 'Department',
			get_query: function() {
				return {
					filters: {
						'is_group' : 1
					}
				}
			}
		},
		{
			fieldname : 'sub_department',
			fieldtype : 'Link',
			label : __('Sub Department'),
			options : 'Department',
			get_query: function() {
				return {
					filters: {
						'is_group' : 0
					}
				}
			}
		},
		{
			fieldname : 'decision_number',
			fieldtype : 'Data',
			label : __('Decision Number'),
		},
		{
			fieldname : 'bank_loan_reference',
			fieldtype : 'Data',
			label : __('Bank Loan Reference'),
		},
	]
};
