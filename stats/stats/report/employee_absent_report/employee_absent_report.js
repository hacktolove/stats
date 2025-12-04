// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Absent Report"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label":__("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			// "reqd":1
		},
		{
			"fieldname": "section",
			"label":__("Section"),
			"fieldtype": "Link",
			"options": "Section ST",
			// "reqd":1
		},
		{
			"fieldname": "main_department",
			"label":__("Main Department"),
			"fieldtype": "Link",
			"options": "Department",
			get_query: function () {
				return {
					query: "stats.api.get_main_department"
				};
			},
		},
		{
			"fieldname": "sub_department",
			"label":__("Sub Department"),
			"fieldtype": "Link",
			"options": "Department",
			get_query: function () {
				return {
					filters: {
						is_group: 0
					}
				};
			},
		},
		{
			"fieldname": "month",
			"label":__("Month"),
			"fieldtype": "Select",
			"options": "January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
			"reqd":1
		}
	]
};
