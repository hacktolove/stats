// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Delay Report"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label":__("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			// "reqd":1
		},
		{
			"fieldname": "custom_section",
			"label":__("Section"),
			"fieldtype": "Link",
			"options": "Section ST",
			// "reqd":1
		},
		{
			"fieldname": "department",
			"label":__("Main Department"),
			"fieldtype": "Link",
			"options": "Department",
			// "reqd":1
		},
		{
			"fieldname": "custom_sub_department",
			"label":__("Sub Department"),
			"fieldtype": "Link",
			"options": "Department",
			// "reqd":1
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