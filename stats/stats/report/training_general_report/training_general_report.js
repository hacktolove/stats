// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Training General Report"] = {
	"filters": [
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
			"fieldname": "employee_no",
			"label":__("Employee No"),
			"fieldtype": "Link",
            "options": "Employee"
		},
		{
			"fieldname": "training_event",
			"label":__("Training Event"),
			"fieldtype": "Link",
			"options": "Training Event ST",
		},
		{
			"fieldname": "training_type",
			"label":__("Training Type"),
			"fieldtype": "Link",
			"options": "Training Type ST",
		},
		{
			"fieldname": "training_classification",
			"label":__("Training Classification"),
			"fieldtype": "Link",
			"options": "Training Classification ST",
		},
		{
			"fieldname": "training_start_date",
			"label":__("Training Start Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "training_level",
			"label":__("Training Level"),
			"fieldtype": "Link",
			"options": "Training Level ST",
		},
		{
			"fieldname": "training_method",
			"label":__("Training Method"),
			"fieldtype": "Select",
			"options": "\nOnline\nAttendance",
		},
		{
			"fieldname": "period",
			"label":__("Period"),
			"fieldtype": "Select",
			"options": "\nMorning\nEvening",
		},
		{
			"fieldname": "city",
			"label":__("City"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "supplier",
			"label":__("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
		},
		{
			"fieldname": "status",
			"label":__("Status"),
			"fieldtype": "Select",
			"options": "\nPending\nAccepted\nRejected\nFinished",
		},
	]
};
