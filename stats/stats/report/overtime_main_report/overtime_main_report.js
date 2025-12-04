// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Overtime Main Report"] = {
	"filters": [
		{
			fieldname: 'from_date',
			fieldtype: 'Date',
			label : __('From Date'),
			default : frappe.datetime.add_months(frappe.datetime.get_today(), month=-1),
			reqd: 1
 		},
		{
			fieldname : 'to_date',
			fieldtype : 'Date',
			label : __('To Date'),
			default : 'Today',
			reqd: 1
 		},
		{
			fieldname: 'main_department',
			fieldtype: 'Link',
			label: __('Main Department'),
			options: 'Department',
			get_query: function() {
				return {
					filters: {
						'is_group' : 1
					}
				}
			}
		},
		{
			fieldname: 'sub_department',
			fieldtype: 'Link',
			label: __('Sub Department'),
			options: 'Department',
			get_query: function() {
				return {
					filters: {
						'is_group' : 0
					}
				}
			}
		},
		{
			fieldname: 'employee',
			fieldtype: 'Link',
			label: __('Employee'),
			options: 'Employee'
		},
		{
			fieldname: 'status',
			fieldtype: 'Select',
			label: __('Status'),
			options: '\nAccepted\nRejected\nPending'
		}
	]
};
