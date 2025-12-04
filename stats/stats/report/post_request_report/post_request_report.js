// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Post Request Report"] = {
	"filters": [
		{
			fieldname : "pr_date",
			fieldtype : "Date",
			label: __('PR Date'),
		},
		{
			fieldname : "request_date",
			fieldtype : "Date",
			label: __('Request Date'),
		},
		{
			fieldname : "employee",
			fieldtype : "Link",
			label: __('Employee'),
			options: "Employee"
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
			fieldname : 'post_type',
			fieldtype : 'Link',
			label : __('Post Type'),
			options : 'Post Type ST'
		}
	]
};
