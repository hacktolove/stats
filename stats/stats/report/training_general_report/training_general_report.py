# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_("No records found"))
		return columns, data
	return columns, data

def get_columns(filters):
	return [
		{
			"fieldname": "employee_name",
			"label":_("Employee Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "main_department",
			"label":_("Main Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": 200
		},
		{
			"fieldname": "sub_department",
			"label":_("Sub Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": 200
		},
		{
			"fieldname": "date",
			"label":_("Date"),
			"fieldtype": "Date",
			"width": 150
		},
		# {
		# 	"fieldname": "employee_no",
		# 	"label":_("Employee No"),
		# 	"fieldtype": "Link",
        #     "options": "Employee"
		# },
		{
			"fieldname": "training_event",
			"label":_("Training Event"),
			"fieldtype": "Link",
			"options": "Training Event ST",
			"width": 200
		},
		{
			"fieldname": "training_type",
			"label":_("Training Type"),
			"fieldtype": "Link",
			"options": "Training Type ST",
			"width": 200
		},
		{
			"fieldname": "training_classification",
			"label":_("Training Classification"),
			"fieldtype": "Link",
			"options": "Training Classification ST",
			"width": 200
		},
		{
			"fieldname": "training_start_date",
			"label":_("Training Start Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "training_end_date",
			"label":_("Training End Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "no_of_days",
			"label":_("No of Days"),
			"fieldtype": "Int",
			"width": 150
		},
		{
			"fieldname": "total_no_of_hours",
			"label":_("Total No of Hours"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "training_level",
			"label":_("Training Level"),
			"fieldtype": "Link",
			"options": "Training Level ST",
			"width": 200
		},
		{
			"fieldname": "training_method",
			"label":_("Training Method"),
			"fieldtype": "Select",
			"options": "\nOnline\nAttendance",
			"width": 150
		},
		{
			"fieldname": "period",
			"label":_("Period"),
			"fieldtype": "Select",
			"options": "\nMorning\nEvening",
			"width": 150
		},
		{
			"fieldname": "city",
			"label":_("City"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "location",
			"label":_("Location"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "employee_checkin_required",
			"label":_("Employee Checkin Required"),
			"fieldtype": "Select",
			"options": "\nYes\nNo",
			"width": 150
		},
		{
			"fieldname": "employee_checkout_required",
			"label":_("Employee Checkout Required"),
			"fieldtype": "Select",
			"options": "\nYes\nNo",
			"width": 150
		},
		{
			"fieldname": "status",
			"label":_("Status"),
			"fieldtype": "Select",
			"options": "\nPending\nAccepted\nRejected\nFinished",
			"width": 150
		},
		{
			"fieldname": "trainer",
			"label":_("Trainer"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "supplier",
			"label":_("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 200
		}		
	]

def get_data(filters):
	conditions = get_conditions(filters)
	training_request_data = frappe.db.sql("""
							SELECT
								tr.employee_no,
								tr.employee_name,
								e.department as main_department,
								e.custom_sub_department as sub_department,
								tr.date,
								tr.training_event,
								tr.training_type,
								tr.training_classification,
								tr.training_start_date,
								tr.training_end_date,
								tr.no_of_days,
								tr.total_of_hours as total_no_of_hours,
								tr.training_level,
								tr.training_method,
								tr.period,
								tr.city,
								tr.location,
								tr.employee_checkin_required,
								tr.employee_checkout_required,
								tr.status,
								tr.trainer,
								tr.supplier
							FROM
								`tabTraining Request ST` tr
							INNER JOIN `tabEmployee` e ON
								e.name = tr.employee_no
							WHERE
								tr.docstatus != 2 {0}
						""".format(conditions), as_dict=True)
	return training_request_data

def get_conditions(filters):
		conditions = ""
		if filters.get("employee_no"):
			conditions += f" and tr.employee_no = '{filters['employee_no']}'"
		if filters.get("sub_department"):
			conditions += f" and e.custom_sub_department = '{filters['sub_department']}'"
		if filters.get("training_event"):
			conditions += f" and tr.training_event = '{filters['training_event']}'"
		if filters.get("training_type"):
			conditions += f" and tr.training_type = '{filters['training_type']}'"
		if filters.get("training_classification"):
			conditions += f" and tr.training_classification = '{filters['training_classification']}'"
		if filters.get("training_start_date"):
			conditions += f" and tr.training_start_date = '{filters['training_start_date']}'"
		if filters.get("training_level"):
			conditions += f" and tr.training_level = '{filters['training_level']}'"
		if filters.get("training_method"):
			conditions += f" and tr.training_method = '{filters['training_method']}'"
		if filters.get("period"):
			conditions += f" and tr.period = '{filters['period']}'"
		if filters.get("city"):
			conditions += f" and tr.city = '{filters['city']}'"
		if filters.get("status"):
			conditions += f" and tr.status = '{filters['status']}'"
		if filters.get("supplier"):
			conditions += f" and tr.supplier = '{filters['supplier']}'"
		return conditions