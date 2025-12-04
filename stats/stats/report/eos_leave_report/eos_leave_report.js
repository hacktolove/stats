// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["EOS Leave Report"] = {
	"filters": [
		{
			fieldname: 'employee',
			fieldtype: 'Link',
			label: __('Employee'),
			options: 'Employee'
		},
		{
			fieldname: 'main_department',
			fieldtype: 'Link',
			label: __('Main Department'),
			options: 'Department',
			get_query: function () {
				return {
					filters: {
						'is_group': true
					}
				}
			}
		},
		{
			fieldname: 'sub_department',
			fieldtype: 'Link',
			label: __('Sub Department'),
			options: 'Department',
			get_query: function () {
				return {
					filters: {
						'is_group': false
					}
				}
			}
		},
		{
			fieldname: 'leave_type',
			fieldtype: 'Link',
			label: __('Leave Type'),
			options: 'Leave Type',
			get_query: function () {
				return {
					query: 'stats.stats.report.eos_leave_report.eos_leave_report.get_leave_type_list',
				}
			}
		}
	]
};