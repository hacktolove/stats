// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Resignation Report"] = {
	"filters": [
		{
			fieldname : "resignation_date",
			fieldtype : 'Date',
			label : __("Resignation Date")
		},
		{
			fieldname : "employee_no",
			fieldtype : 'Link',
			label : __("Employee No"),
			options : "Employee"
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
			fieldname : 'section',
			fieldtype : 'Link',
			label : __('Section'),
			options : 'Section ST'
		},
		{
			fieldname : 'branch',
			fieldtype : 'Link',
			label : __('Branch'),
			options : 'Branch'
		}
	]
};
