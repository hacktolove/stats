// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Account Wise Report"] = {
	"filters": [
		{
			"fieldname": "fiscal_year",
			"label":__("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
            "default":  erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
			"reqd": 1
		},
		{
			"fieldname": "cost_center_wise",
			"label": __("Cost Center Wise"),
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname": "cost_center",
			"label":__("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"depends_on": "eval:doc.cost_center_wise==1",
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
	]
};
