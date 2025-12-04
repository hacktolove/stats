// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Attendance Report"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label":__("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		},
		{
			"fieldname": "section",
			"label":__("Section"),
			"fieldtype": "Link",
			"options": "Section ST",
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
			"fieldname": "from_date",
			"label":__("From Date"),
			"fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.nowdate(), -30),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label":__("To Date"),
			"fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
			"reqd": 1
		}
	]
};
