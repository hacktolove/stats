// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Leave Application Report"] = {
	"filters": [
		// {
		// 	fieldname: 'from_date',
		// 	fieldtype: 'Date',
		// 	label : __('From Date'),
		// 	default : frappe.datetime.add_months(frappe.datetime.get_today(), month=-1),
		// 	reqd: 1
 		// },
		// {
		// 	fieldname : 'to_date',
		// 	fieldtype : 'Date',
		// 	label : __('To Date'),
		// 	default : 'Today',
		// 	reqd: 1
 		// },
		{
			fieldname: 'employee',
			fieldtype: 'Link',
			label: __('Employee'),
			options: 'Employee'
		},
		{
			fieldname: 'section',
			fieldtype: 'Link',
			label: __('Section'),
			options: 'Section ST'
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
			fieldname: 'workflow_status',
			fieldtype: 'Link',
			label: __('Workflow Status'),
			options: 'Workflow State'
		},
		{
			fieldname: 'leave_application_status',
			fieldtype: 'Select',
			label: __('Leave Application Status'),
			options: '\nOpen\nApproved\nRejected\nCancelled'
		},
		{
			fieldname: 'leave_request_status',
			fieldtype: 'Select',
			label: __('Leave Request Status'),
			options: '\nApproved\nRejected\nPending'
		},
		{
			fieldname: 'leave_type',
			fieldtype: 'Link',
			label: __('Leave Type'),
			options: 'Leave Type'
		},
		{
			fieldname: 'contract',
			fieldtype: 'Select',
			label: __('Contract'),
			options: '\nCivil\nDirect'
		}
	]
};
