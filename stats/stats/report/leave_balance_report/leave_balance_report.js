// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Leave Balance Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label":__("From Date"),
			"fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.nowdate(), -30),
			"readonly":1
		},
		{
			"fieldname": "to_date",
			"label":__("To Date"),
			"fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
			"readonly":1
		},
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
	]
};
fiscal_year =  erpnext.utils.get_fiscal_year(frappe.datetime.get_today())
frappe.db.get_value("Fiscal Year", fiscal_year, ['year_start_date','year_end_date'])
    .then(r => {
		console.log(r,"r")
        frappe.query_report.set_filter_value("from_date", r.message.year_start_date) 
		frappe.query_report.set_filter_value("to_date", r.message.year_end_date) 
    })