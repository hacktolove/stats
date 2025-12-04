// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Salary Structure Report"] = {
	"filters": [
		{
			"fieldname": "id",
			"label":__("ID"),
			"fieldtype": "Link",
			"options": "Salary Structure"
		},
		{
			"fieldname": "is_active",
			"label":__("Is Active"),
			"fieldtype": "Select",
			"options": ["","Yes", "No"],
		},
		
	]
};
