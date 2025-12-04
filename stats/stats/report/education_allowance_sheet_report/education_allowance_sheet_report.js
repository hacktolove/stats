// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Education Allowance Sheet Report"] = {
	"filters": [
		{
			fieldname : 'emp_no',
			fieldtype : 'Link',
			label : __("Employee"),
			options : 'Employee'
		},
		{
			fieldname : 'sub_department',
			fieldtype : 'Link',
			label : __("Sub Department"),
			options : 'Department'
		}
	]
};
