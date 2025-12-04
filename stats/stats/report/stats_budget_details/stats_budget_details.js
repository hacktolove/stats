// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Stats Budget Details"] = {
	"filters": [
		{
			"fieldname": "fiscal_year",
			"label":__("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
            "default":  erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
			// "reqd": 1
		},
		{
			"fieldname": "cost_center",
			"label":__("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			get_query: function () {
				const default_company = frappe.defaults.get_default("company");
				return {
					filters: {
						"company": default_company,
						"is_group": 0,
						"disabled": 0
					}
				};
			},
		},
		{
			"fieldname": "account",
			"label":__("Account"),
			"fieldtype": "Link",
			"options": "Account",
			get_query: function () {
				const default_company = frappe.defaults.get_default("company");
				return {
					filters: {
						"company": default_company,
						"is_group": 0,
						"account_type": ["in",["Expense Account", "Indirect Expense"]]
					}
				};
			},
		}
	]
};
