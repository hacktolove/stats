# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _
from frappe.utils import cstr,flt


def execute(filters=None,msgprint=1):

	columns, data = [], []

	columns = get_columns(filters)
	data, report_summary=get_attendance_data(filters)

	if not data:
		if msgprint==1:
			frappe.msgprint(_("No records found"))
			return columns, data
	note = """<ol>
	<li>for weeklyoff (fri/sat) and company holiday,there is NO  attendance record</li>
	<li>for On Leave(Paid),In Training,Business Trip,Scholarship, auto attendance is created with Net Working Minutes</li>
	<li>irrespective of month, expected total monthly hours is fixed ex 160 or 170 hours</li>
	<li>for absent and LWP, attendance record is created. In salary there is additional salary deduction component for both</li>
	<li>He has come for 2 hours only, so he is absent and that 2 hours will NOT be counted to cover shortage</li>
	<li>Shortfall = Expected(w/o weekoff) ex 160 -- Company Holidays -- LWP+Absent(as already deducted) -- sum(Net Working Minutes for Present+Paid Leaves)  </li>
	</ol>"""
	return columns, data, note, None, report_summary


def get_columns(filters):
	return [
		{
			"fieldname": "attendance",
			"label":_("Attendance"),
			"fieldtype": "Link",
			"options": "Attendance",
			"width":"200"
		},
		{
			"fieldname": "employee",
			"label":_("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width":"200"
		},
		{
			"fieldname": "in_time",
			"label":_("In"),
			"fieldtype": "Datetime",
			"width":"200"
		},
		{
			"fieldname": "out_time",
			"label":_("Out"),
			"fieldtype": "Datetime",
			"width":"200"
		},
		{
			"fieldname": "status",
			"label":_("Status"),
			"fieldtype": "Data",
			"width":"200"
		},
		{
			"fieldname": "working_minutes_per_day",
			"label":_("Expected"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "actual_working_minutes",
			"label":_("Actual"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "net_working_minutes",
			"label":_("Net"),
			"fieldtype": "Int",
			"width":"100"
		},
		# {
		# 	"fieldname": "difference_in_working_minutes",
		# 	"label":_("Diff"),
		# 	"fieldtype": "Int",
		# 	"width":"100"
		# },
		{
			"fieldname": "reconciliation_method",
			"label":_("Reconciliation Method"),
			"fieldtype": "Data",
			"width":"200"
		},
		{
			"fieldname": "extra_minutes",
			"label":_("Extra Minutes"),
			"fieldtype": "Int",
			"width":"100"
		},
		# {
		# 	"fieldname": "actual_delay",
		# 	"label":_("Actual Delay"),
		# 	"fieldtype": "Int",
		# 	"width":"100"
		# },
		# {
		# 	"fieldname": "actual_early",
		# 	"label":_("Actual Early"),
		# 	"fieldtype": "Int",
		# 	"width":"100"
		# }
	]

def get_attendance_data(filters):
	conditions = get_conditions(filters)

	attendance_data = frappe.db.sql("""
				SELECT
					name as attendance,
					employee,
					employee_name,
					in_time,
					out_time,
					custom_attendance_type as status,
					custom_working_minutes_per_day as working_minutes_per_day,
					custom_actual_working_minutes as actual_working_minutes,
					custom_net_working_minutes as net_working_minutes,
					# custom_difference_in_working_minutes as difference_in_working_minutes,
					custom_reconciliation_method as reconciliation_method,
					# custom_actual_delay_minutes as actual_delay,
					# custom_actual_early_minutes as actual_early,
					custom_extra_minutes as extra_minutes
				from
					`tabAttendance`
				where {0}
		 """.format(conditions),filters,as_dict=1,debug=1)

	convert_mins_days=0
	employee_contract_name = frappe.db.get_value("Employee",filters.employee,"custom_contract_type")
	if employee_contract_name:
		total_hours_per_day = frappe.db.get_value("Contract Type ST",employee_contract_name,["total_hours_per_day"])
		if total_hours_per_day:
			convert_mins_days=60*total_hours_per_day
				
	if convert_mins_days==0:
		frappe.throw(_("Please set total_hours_per_day for contract type {0}".format(employee_contract_name)))
	expected_total_monthly_minutes= get_expected_total_monthly_minutes_and_total_minutes_per_day(filters.employee)
	value_expected_total_monthly_minutes=cstr(expected_total_monthly_minutes) +'m '+ cstr(flt(expected_total_monthly_minutes/(convert_mins_days),1))+'d'
	company_holiday_total_monthly_mins = get_company_holiday_count(filters.employee, filters.from_date, filters.to_date)
	value_company_holiday_total_monthly_mins=cstr(company_holiday_total_monthly_mins) +'m '+ cstr(flt(company_holiday_total_monthly_mins/(convert_mins_days),1))+'d'	
	lwp_absent_total_monthly_mins=get_lwp_absent_total_monthly_mins(filters)
	value_lwp_absent_total_monthly_mins=cstr(lwp_absent_total_monthly_mins) +'m '+ cstr(flt(lwp_absent_total_monthly_mins/(convert_mins_days),1))+'d'
	present_total_monthly_mins = get_total_present_minutes_per_month(filters)
	if present_total_monthly_mins:
		value_present_total_monthly_mins=cstr(present_total_monthly_mins) +'m '+ cstr(flt(present_total_monthly_mins/(convert_mins_days),1))+'d'
	else:
		value_present_total_monthly_mins=0
	incomplete_total_monthly_minutes= cstr(calculate_incomplete_total_monthly_minutes(filters.employee, filters.from_date, filters.to_date))+'m'

	report_summary=[
		{'label':'Exp Month Mins(W/O Week Off,Fixed)','value':value_expected_total_monthly_minutes},
		{'type':'separator','value':'-'},
		{'label':'Holiday Mins(Paid)','value':value_company_holiday_total_monthly_mins},		
		{'type':'separator','value':'-'},
		{'label':'LWP+Absent Mins(Deducted)','value':value_lwp_absent_total_monthly_mins},		
		{'type':'separator','value':'-'},		
		{'label':'Present Mins(Present+Paid Leaves)','value':value_present_total_monthly_mins},
		{'type':'separator','value':'='},
		{'label':'Shortfall Working Mins(will cut in salary)','value':incomplete_total_monthly_minutes}		
	]
	return attendance_data,report_summary

def get_conditions(filters):
	conditions =""
	
	if filters.from_date:
		conditions += "attendance_date >= %(from_date)s "
	
	if filters.to_date:
		conditions += "and attendance_date <= %(to_date)s"

	if filters.employee:
		conditions += "and employee = %(employee)s "

	return conditions

@frappe.whitelist()
def get_company_holiday_count(employee, from_date, to_date):
	company_holiday_count = 0
	current_holiday_list = frappe.db.get_all("Holiday List",
										filters={"from_date":["<=",from_date],"to_date":[">=",to_date]},
										fields=["name"])
	if len(current_holiday_list)>0:
		company_holidays = frappe.db.get_all("Holiday",
										parent_doctype="Holiday List",
										filters={"parent":current_holiday_list[0].name,"weekly_off":0,"holiday_date":["between",[from_date,to_date]]},
										fields=["name"])
		if len(company_holidays)>0:
			company_holiday_count = company_holiday_count + len(company_holidays)

		employee_contract_name = frappe.db.get_value("Employee",employee,"custom_contract_type")
		if employee_contract_name:
			total_minutes_per_day = frappe.db.get_value("Contract Type ST",employee_contract_name,["total_mins_per_day"])
			company_holiday_minutes = company_holiday_count * total_minutes_per_day
	return company_holiday_minutes

@frappe.whitelist()
def get_lwp_absent_total_monthly_mins(filters):
	# if any change in logic, please compare it with payroll entry deduction logic
	conditions = get_conditions(filters)
	employee_contract_name = frappe.db.get_value("Employee",filters.employee,"custom_contract_type")
	if employee_contract_name:
		total_mins_per_day = frappe.db.get_value("Contract Type ST",employee_contract_name,["total_mins_per_day"])
		

	lwp_absent_total_monthly_min = frappe.db.sql("""
				SELECT
					count(name) as mins
				from
					`tabAttendance`
				where {0} 
					and ((custom_attendance_type ='On LWP' and status = 'On Leave')
					or (custom_attendance_type ='Absent' and status ='Absent'))										  
		""".format(conditions),filters,as_dict=1,debug=1)
	if len(lwp_absent_total_monthly_min)>0:
		lwp_absent_total_monthly_min = lwp_absent_total_monthly_min[0].mins * total_mins_per_day
	return lwp_absent_total_monthly_min

@frappe.whitelist()
def get_total_present_minutes_per_month(filters):
	
	conditions = get_conditions(filters)
	total_monthly_mins = frappe.db.sql("""
				SELECT
					sum(custom_working_minutes_with_grace) as mins
				from
					`tabAttendance`
				where {0} 
					and custom_attendance_type in ('Present', 'On Leave', 'In Training', 'Business Trip', 'Scholarship', 'Present Due To Reconciliation')
					and status in ('Present','On Leave')
		""".format(conditions),filters,as_dict=1,debug=1)
	if len(total_monthly_mins)>0:
		present_total_monthly_mins = total_monthly_mins[0].mins
	return present_total_monthly_mins

@frappe.whitelist()
def get_expected_total_monthly_minutes_and_total_minutes_per_day(employee):
	employee_contract_name = frappe.db.get_value("Employee",employee,"custom_contract_type")
	if employee_contract_name:
		expected_monthly_minutes = frappe.db.get_value("Contract Type ST",employee_contract_name,["total_mins_per_month"])
		return expected_monthly_minutes

@frappe.whitelist()	
def calculate_incomplete_total_monthly_minutes(employee, from_date, to_date):
	actual_total_monthly_mins=0
	incomplete_total_monthly_mins=0
	filters=frappe._dict({"employee":employee, "from_date":from_date, "to_date":to_date})
	expected_monthly_minutes= get_expected_total_monthly_minutes_and_total_minutes_per_day(employee)

	company_holiday_total_monthly_mins = get_company_holiday_count(employee,from_date,to_date)
	if company_holiday_total_monthly_mins:
		actual_total_monthly_mins=actual_total_monthly_mins+company_holiday_total_monthly_mins
	lwp_absent_total_monthly_mins=get_lwp_absent_total_monthly_mins(filters)
	if lwp_absent_total_monthly_mins:
		actual_total_monthly_mins=actual_total_monthly_mins+lwp_absent_total_monthly_mins
	present_total_minutes_per_month = get_total_present_minutes_per_month(filters)
	if present_total_minutes_per_month:
		actual_total_monthly_mins =actual_total_monthly_mins+ present_total_minutes_per_month

	incomplete_total_monthly_mins = expected_monthly_minutes - actual_total_monthly_mins
	return incomplete_total_monthly_mins