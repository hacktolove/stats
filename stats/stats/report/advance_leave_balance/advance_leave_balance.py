# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, today, month_diff, getdate
from erpnext.accounts.utils import get_fiscal_year
from stats.api import get_quater_start_end_date_from_current_date
from hrms.hr.doctype.leave_application.leave_application import get_number_of_leave_days


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	notes = _("<b>Note:</b><br>1) Leave taken end date should be less than equal to Balance At i..e Leave Application To date is compared with Balance At <br>2) If the <b>Monthly Leave Balance</b> is set in contract type ST, then monthly leave will be deducted based on Balance At Date.<br>3) Balance value calculation : i.e Balance At = '30-06-2025' and Today = '06-08-2025'...then will deduct monthly balance of july only")
	return columns, data, notes

def get_columns(filters):
	return [
		{
			"fieldname": "employee",
			"fieldtype": "Link",
			"label": _("Employee No"),
			"options": "Employee",
			"width": 200
		},
		{
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"label": _("Employee Name"),
			"width": 200
		},
		{
			"fieldname": "main_department",
			"fieldtype": "Link",
			"label":_("Main Department"),
			"options": "Department",
			"width": 200
		},
		{
			"fieldname": "sub_department",
			"fieldtype": "Link",
			"label":_("Sub Department"),
			"options": "Department",
			"width": 200
		},
		{
			"fieldname": "idresidency_number",
			"fieldtype": "Data",
			"label":_("ID/Residency No"),
			"width": 300
		},
		{
			"fieldname": "contract_type",
			"fieldtype": "Link",
			"label": _("Contract Type"),
			"options": "Contract Type ST",
			"width": 200
		},
		{
			"fieldname": "contract",
			"fieldtype": "Select",
			"label": _("Contract"),
			"options": "Civil\nDirect",
			"width": 200
		},
		{
			"fieldname": 'leave_type',
			"fieldtype": 'Link',
			"label": _('Leave Type'),
			"options": 'Leave Type',
			"width": 200
		},
		{
			"fieldname": "balance_at_date",
			"fieldtype": "Float",
			"label":_("Balance At Date"),
			"width": 100
		},
		{
			"fieldname": "consumed_leaves",
			"fieldtype": "Float",
			"label":_("Consumed Leaves (In Quarter)"),
			"width": 250
		}
	]

def get_data(filters):
	conditions=get_conditions(filters)

	employee_details = frappe.db.sql("""
						SELECT
							e.name as employee,
							e.employee_name,
							e.department as main_department,
							e.custom_sub_department as sub_department,
							e.custom_idresidency_number as idresidency_number,
							e.custom_contract_type as contract_type,
							ct.contract_type as contract,
							lall.name,
							lall.leave_type,
							lall.total_leaves_allocated 
						FROM
							`tabEmployee` e
						LEFT OUTER JOIN `tabContract Type ST` ct ON 
							e.custom_contract_type = ct.name
						INNER JOIN `tabLeave Allocation` lall ON
							e.name = lall.employee
						WHERE
							lall.docstatus = 1 {0}
					""".format(conditions),as_dict=True,debug=1)

	if len(employee_details)>0:
		balance = 0
		for row in employee_details:
			balance_at_date = 0
			consumed_in_quater = 0
			allocated_days = row.total_leaves_allocated
			if allocated_days:
				balance_date = filters.get("balance_at")
				leaves_to_be_deduct = 0
				if getdate(today()).month != getdate(balance_date).month:
					months = month_diff(today(),balance_date)

					### deduct leave in multiplication of month difference from balance date till today ( i.e Balance At = '30-06-2025' and Today = '06-08-2025'...then will deduct monthly balance of july only)

					monthly_leaves = frappe.db.get_value("Contract Type ST",row.contract_type,"monthly_leave_balance")
					if monthly_leaves>0:
						leaves_to_be_deduct = monthly_leaves * (months-2)
						
				balance_at_date = allocated_days - leaves_to_be_deduct
				
				current_fiscal_year = get_fiscal_year(today())[0]
				fiscal_year_start_date, fiscal_year_end_date = frappe.db.get_value("Fiscal Year",current_fiscal_year,["year_start_date","year_end_date"])

				### get all leave application of current fiscal year --> This calculation is for Leave Balance At Balance Date (Balance date is from filters)

				leave_applicaion_list = frappe.db.get_all("Leave Application",
											  filters={"docstatus":1, "status":"Approved", "employee":row.employee, "leave_type":row.leave_type, "from_date":[">=",fiscal_year_start_date], "to_date":["<=",fiscal_year_end_date]},
											  fields=["total_leave_days", "name", "from_date", "to_date"],
											  order_by="from_date asc")
				
				if len(leave_applicaion_list)>0:
					for application in leave_applicaion_list:
						if getdate(application.from_date) <= getdate(balance_date) and getdate(application.to_date) >= getdate(balance_date):
							balance_at_date = balance_at_date - get_number_of_leave_days(row.employee, row.leave_type, getdate(application.from_date), getdate(balance_date))
						elif getdate(application.from_date) <= getdate(balance_date) and getdate(application.to_date) <= getdate(balance_date):
							balance_at_date = balance_at_date - application.total_leave_days

				### Calculate Quarterly Comsumed Leaves

				quater_start_date, quater_end_date = get_quater_start_end_date_from_current_date(filters.get("balance_at"))
				if quater_start_date and quater_end_date:
					leave_application_belong_to_quater = frappe.db.get_all("Leave Application",
															filters={"docstatus":1,"status":"Approved","leave_type":row.leave_type,"employee":row.employee},
															or_filters=[{"from_date":["between", [quater_start_date, quater_end_date]]}, {"to_date":["between", [quater_start_date, quater_end_date]]}],
															fields=["total_leave_days", "name", "from_date", "to_date"],
															order_by="from_date asc")
					
					if len(leave_application_belong_to_quater)>0:
						for leave_application in leave_application_belong_to_quater:
							if getdate(leave_application.from_date) >= getdate(quater_start_date) and getdate(leave_application.to_date) <= getdate(quater_end_date):
								consumed_in_quater = consumed_in_quater + leave_application.total_leave_days
								
							elif getdate(leave_application.from_date) <= getdate(quater_start_date) and getdate(leave_application.to_date) <= getdate(quater_end_date):
								consumed_in_quater = consumed_in_quater + get_number_of_leave_days(row.employee, row.leave_type, quater_start_date, leave_application.to_date)
								
							elif getdate(leave_application.from_date) >= getdate(quater_start_date) and getdate(leave_application.to_date) >= getdate(quater_end_date):
								consumed_in_quater = consumed_in_quater + get_number_of_leave_days(row.employee, row.leave_type, leave_application.from_date, quater_end_date)
					
					### Leave Application Belongs to Multiple Quarter
					
					leave_application_within_multiple_quarter = frappe.db.get_all("Leave Application",
																   filters={"docstatus":1,"status":"Approved","leave_type":row.leave_type,"employee":row.employee,"from_date":["<=", quater_start_date],"to_date":[">=", quater_end_date]},
																   fields=["total_leave_days", "name", "from_date", "to_date"],
																   order_by="from_date asc")
					if len(leave_application_within_multiple_quarter)>0:
						for l_application in leave_application_within_multiple_quarter:
							consumed_in_quater = consumed_in_quater + get_number_of_leave_days(row.employee, row.leave_type, quater_start_date, quater_end_date)
			
			row["balance_at_date"]=balance_at_date
			row["consumed_leaves"]=consumed_in_quater
				
			
	return employee_details

def get_conditions(filters):
	conditions = ""
	if filters.get("balance_at"):
		if filters.get("balance_at") > today():
			frappe.throw(_("You can not select future dates."))
		else :
			conditions += "and lall.from_date <= '{0}' and lall.to_date >= '{0}'".format(filters.get("balance_at"))
	if filters.get("employee"):
		conditions += "and lall.employee = '{0}'".format(filters.get("employee"))	
	if filters.get("main_department"):
		conditions += " and e.department = '{0}'".format(filters.get("main_department"))
	if filters.get("sub_department"):
		conditions += " and e.custom_sub_department = '{0}'".format(filters.get("sub_department"))
	if filters.get("leave_type"):
		conditions += "and lall.leave_type = '{0}'".format(filters.get("leave_type"))
	
	return conditions