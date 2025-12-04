// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Advance Leave Balance"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label":__("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
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
			"fieldname": "leave_type",
			"label":__("Leave Type"),
			"fieldtype": "Link",
			"options": "Leave Type",
			"reqd":1,
			get_query: function () {
				return {
					query: "stats.hr_utils.get_annual_leave_from_contract_type"
				};
			},
		},
		{
			"fieldname": "balance_at",
			"label":__("Balance At"),
			"fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
			"readonly":1
		},
	]
};
