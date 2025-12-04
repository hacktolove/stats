// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Overtime Amount Department Wise Report"] = {
	"filters": [
		{
			fieldname: 'from_date',
			fieldtype: 'Date',
			label : __('From Date'),
			default : frappe.datetime.add_months(frappe.datetime.get_today(), month=-1),
 		},
		{
			fieldname : 'to_date',
			fieldtype : 'Date',
			label : __('To Date'),
			default : 'Today',
 		},
		{
			fieldname : 'based_on',
			fieldtype : 'Select',
			label : __('Based On'),
			options : '\nMain Department\nSub Department',
			reqd:1
		},
	]
};
