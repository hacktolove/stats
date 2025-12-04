// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Payment Request Report"] = {
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
			fieldname: 'reference',
			fieldtype: 'Select',
			label: __('Reference Name'),
			options: '\nOvertime Sheet ST\nBusiness Trip Sheet ST\nEnd Of Service Sheet ST\nEmployee Reallocation Sheet ST\nEducation Allowance Sheet ST\nDue Vacation Sheet'
		}
	]
};
