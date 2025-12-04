// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["General Attendance Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label":__("From Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.month_start(),
			"reqd":1
		},
		{
			"fieldname": "to_date",
			"label":__("To Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.month_end(),
			"reqd":1
		},
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
		}
	]
};
