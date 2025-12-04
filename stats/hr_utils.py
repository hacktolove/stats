import frappe
from frappe import _
from hrms.hr.doctype.leave_application.leave_application import get_holidays
from stats.stats.report.stats_budget_details.stats_budget_details import get_data
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import today, flt, getdate, nowdate, add_to_date, date_diff, get_datetime, cstr, get_link_to_form, formatdate, cint
from erpnext.setup.doctype.employee.employee import is_holiday
from hrms.hr.doctype.shift_assignment.shift_assignment import get_employee_shift
from hijridate import Hijri, Gregorian

def check_if_holiday_between_applied_dates(employee, from_date, to_date, holiday_list=None):
	holidays = get_holidays(employee, from_date, to_date, holiday_list=holiday_list)
	print(holidays,"/////////////////////")
	# print(holidays, '-----holiday b/w')
	if holidays > 0:
		return True
	else: return False

def check_employee_in_scholarship(employee, from_date, to_date=None):
	if not to_date:
		to_date=from_date

	scholarship = frappe.qb.DocType('Scholarship Request ST')
	scholarship_processing = frappe.qb.DocType('Scholarship Requests Processing ST')
	scholarship_request = frappe.qb.DocType('Scholarship Request Details ST')
	
	overlapping_scholarship = (
	frappe.qb.from_(scholarship)
			.select(scholarship.name)
			.inner_join(scholarship_request)
			.on(scholarship.name == scholarship_request.scholarship_request_reference)
			.inner_join(scholarship_processing)
			.on(scholarship_request.parent == scholarship_processing.name)
			.where(
				(scholarship.employee_no == employee)
				& (scholarship.docstatus < 2)
				& (to_date >= scholarship_processing.scholarship_start_date)
				& (from_date <= scholarship_processing.scholarship_end_date)
				& (scholarship.acceptance_status == "Accepted")
			)
		).run(as_dict=True)
	
	# print(overlapping_scholarship, '--overlapping_scholarship')
	if overlapping_scholarship:
		return True
	else: return False

def check_employee_in_training(employee,from_date, to_date=None):
	if not to_date:
		to_date=from_date

	training = frappe.qb.DocType('Training Request ST')
	overlapping_training = (
	frappe.qb.from_(training)
			.select(training.name)
			.where(
				(training.employee_no == employee)
				& (training.docstatus < 2)
				& (to_date >= training.training_start_date)
				& (from_date <= training.training_end_date)
				& (training.status == "Accepted")
			)
		).run(as_dict=True)
	
	# print(overlapping_training, '--overlapping_training')
	if overlapping_training:
		return True
	else: return False

def check_employee_in_salary_freezing(employee,from_date, to_date=None):
	if not to_date:
		to_date=from_date

	salary_freezing = frappe.qb.DocType('Salary Freezing ST')
	overlapping_salary_freezing = (
	frappe.qb.from_(salary_freezing)
			.select(salary_freezing.name)
			.where(
				(salary_freezing.employee_no == employee)
				& (salary_freezing.docstatus < 2)
				& (to_date >= salary_freezing.salary_freezing_start_date)
				& (from_date <= salary_freezing.salary_freezing_end_date)
				& (salary_freezing.decision_number.isnull() == 0)
			)
		).run(as_dict=True)
	
	print(overlapping_salary_freezing, '--overlapping_salary_freezing')
	if overlapping_salary_freezing:
		return True
	else: return False

def check_available_amount_for_budget(budget_account,cost_center):
	fiscal_year = get_fiscal_year(today())[0]
	filters=frappe._dict({'fiscal_year': fiscal_year, 'cost_center': cost_center, 'account': budget_account})
	budget = get_data(filters)

	if len(budget) > 0:
		return budget[0].get("available")
	else:
		return


def get_latest_total_monthly_salary_of_employee(employee):
	employee_monthly_salary = frappe.db.get_all("Salary Structure Assignment", filters={"employee":employee, "from_date": ["<=", today()], "docstatus":1}, 
												fields=["base"],
												order_by= "from_date desc",
												limit=1)
	
	print(employee_monthly_salary, '--employee_monthly_salary')
	
	if len(employee_monthly_salary) > 0:
		return employee_monthly_salary[0].base
	else: 
		return

def validate_dates(employee, from_date, to_date):
	date_of_joining, relieving_date = frappe.db.get_value(
		"Employee", employee, ["date_of_joining", "relieving_date"]
	)
	if getdate(from_date) > getdate(to_date):
		frappe.throw(_("To date can not be less than from date"))
	elif date_of_joining and getdate(from_date) < getdate(date_of_joining):
		frappe.throw(_("From date can not be less than employee's joining date"))
	elif relieving_date and getdate(to_date) > getdate(relieving_date):
		frappe.throw(_("To date can not greater than employee's relieving date"))
		  
@frappe.whitelist()
def get_employee_emails(details):
	email_id_list = []
	for row in details:
		email_id_list.append(row.email_id)

	combine_email_id = ",".join((ele if ele!=None else '') for ele in email_id_list)
	return combine_email_id  

@frappe.whitelist()
def set_yearly_permission_balance_in_employee_profile():
	employees=frappe.db.get_list('Employee', filters={'status': ['=', 'Active']})
	for employee in employees:
		emp_doc=frappe.get_doc("Employee",employee)
		custom_contract_type=emp_doc.custom_contract_type
		contract = frappe.db.get_value('Contract Type ST', custom_contract_type, 'contract')
		if contract == "Direct":
			yearly_permission_balance = frappe.db.get_value('Contract Type ST', custom_contract_type, 'permission_balance_per_year')
			emp_doc.custom_permission_balance_per_year=yearly_permission_balance
			emp_doc.add_comment("Comment", text='Permission Balance Per Yearis set to {0} on {1} by system.'.format(yearly_permission_balance,nowdate()))
			emp_doc.save(ignore_permissions=True)

def get_no_of_day_between_dates(report_start_date, report_end_date, doctype_start_date, doctype_end_date,employee):
	no_of_days = 0
	diff_of_applied_dates = date_diff(doctype_end_date,doctype_start_date)+1
	if report_start_date and report_end_date and doctype_start_date and doctype_end_date:
		if doctype_start_date>=report_start_date and doctype_end_date<=report_end_date:
			print("1")
			for day in range(diff_of_applied_dates):
				next_date = add_to_date(doctype_start_date,days=day)
				holiday = is_holiday(employee,next_date)
				if holiday==False:
					no_of_days = no_of_days + 1

		elif doctype_start_date >= report_start_date and doctype_end_date>report_end_date:
			print("2")
			for day in range(diff_of_applied_dates):
				next_date = add_to_date(doctype_start_date,days=day)
				holiday = is_holiday(employee,next_date)
				if holiday==False:
					if next_date<=report_end_date:
						no_of_days = no_of_days + 1
			
		elif doctype_start_date < report_start_date and doctype_end_date <= report_end_date:
			print("3")
			for day in range(diff_of_applied_dates):
				next_date = add_to_date(doctype_start_date,days=day)
				holiday = is_holiday(employee,next_date)
				if holiday==False:
					if next_date>=report_start_date and next_date<=report_end_date:
						no_of_days = no_of_days + 1
		
		else :
			print("4")
			for day in range(diff_of_applied_dates):
				next_date = add_to_date(doctype_start_date,days=day)
				holiday = is_holiday(employee,next_date)
				if holiday==False:
					if next_date>=report_start_date and next_date<=report_end_date:
						no_of_days = no_of_days + 1
	return no_of_days

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_leave_type_for_allow_after_consuming_balance(doctype, txt, searchfield, start, page_len, filters):
	baby_leaves = frappe.db.get_value("Stats Settings ST", "Stats Settings ST", ["new_baby_leave_type","baby_extended_leave_type", "baby_health_leave_type"])
	print(baby_leaves, "----baby_leaves")
	leave_type_list = frappe.db.get_all("Leave Type", filters={"name": ("like", f"{txt}%")}, fields=["name","is_lwp"])
	leave_type_list_without_baby_leaves = []
	if len(leave_type_list) > 0:
		for leave_type in leave_type_list:
			if leave_type.name not in baby_leaves:
				if leave_type.is_lwp == 0:
					leave_type_list_without_baby_leaves.append(leave_type.name)

	unique_leave_type = tuple((i,) for i in leave_type_list_without_baby_leaves)
	return unique_leave_type

def is_leave_year_valid(leave_start_date, leave_end_date, employee):
	leave_year_exists = ""
	leave_cycle_start_date, leave_cycle_end_date = frappe.db.get_value("Employee",employee,["custom_leave_cycle_start_date","custom_leave_cycle_end_date"])
	print(leave_cycle_start_date, leave_cycle_end_date,"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++leave_cycle_start_date, leave_cycle_end_date")
	if leave_cycle_start_date==None and leave_cycle_end_date==None:
		leave_year_exists = "Not Define"
	if leave_cycle_start_date and leave_cycle_end_date:
		print(leave_cycle_start_date and leave_cycle_end_date, leave_cycle_start_date ,leave_cycle_end_date,"========leave_cycle_start_date and leave_cycle_end_date")
		leave_year_exists = "Exists"
	if leave_cycle_start_date and leave_cycle_end_date:
		if getdate(leave_start_date)>getdate(leave_cycle_end_date) and getdate(leave_end_date)>getdate(leave_cycle_end_date):
			leave_year_exists = "Future Dates"
		if getdate(leave_start_date)<=getdate(leave_cycle_end_date) and getdate(leave_end_date)>getdate(leave_cycle_end_date):
			leave_year_exists = "Accross The Year"

	return leave_year_exists, leave_cycle_start_date, leave_cycle_end_date

def is_fatal_leave_cycle_year_valid(leave_start_date, leave_end_date, employee):
	leave_year_exists = ""
	leave_cycle_start_date, leave_cycle_end_date = frappe.db.get_value("Employee",employee,["custom_fatal_leave_cycle_start_date","custom_fatal_leave_cycle_end_date"])
	print(leave_cycle_start_date, leave_cycle_end_date,"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++leave_cycle_start_date, leave_cycle_end_date")
	if leave_cycle_start_date==None and leave_cycle_end_date==None:
		leave_year_exists = "Not Define"
	if leave_cycle_start_date and leave_cycle_end_date:
		print(leave_cycle_start_date and leave_cycle_end_date, leave_cycle_start_date ,leave_cycle_end_date,"========leave_cycle_start_date and leave_cycle_end_date")
		leave_year_exists = "Exists"
	if leave_cycle_start_date and leave_cycle_end_date:
		print("leave date exists")
		print(leave_start_date, leave_end_date,"========leave_start_date, leave_end_date",leave_cycle_start_date,leave_cycle_end_date)
		if getdate(leave_start_date)>getdate(leave_cycle_end_date) and getdate(leave_end_date)>getdate(leave_cycle_end_date):
			leave_year_exists = "Future Dates"
		if getdate(leave_start_date)<=getdate(leave_cycle_end_date) and getdate(leave_end_date)>getdate(leave_cycle_end_date):
			leave_year_exists = "Accross The Year"
	
	return leave_year_exists, leave_cycle_start_date, leave_cycle_end_date

def is_leave_applied_dates_within_leave_cycle_year(leave_start_date, leave_end_date, employee, leave_type=None):
	if leave_type=="Sick Leave":
		leave_cycle_start_date, leave_cycle_end_date = frappe.db.get_value("Employee",employee,["custom_leave_cycle_start_date","custom_leave_cycle_end_date"])
		if leave_cycle_start_date and leave_cycle_end_date:
			print(leave_cycle_start_date,leave_cycle_end_date,"==",leave_start_date, leave_end_date)
			if getdate(leave_cycle_start_date) <= getdate(leave_start_date) and getdate(leave_cycle_end_date) >= getdate(leave_end_date):
				return True
			else : 
				return False
	elif leave_type=="Fatal Sick Leave":
		fatal_leave_cycle_start_date, fatal_leave_cycle_end_date = frappe.db.get_value("Employee",employee,["custom_fatal_leave_cycle_start_date","custom_fatal_leave_cycle_end_date"])
		if fatal_leave_cycle_start_date and fatal_leave_cycle_end_date:
			print(fatal_leave_cycle_start_date,fatal_leave_cycle_end_date,"==",leave_start_date, leave_end_date)
			if getdate(fatal_leave_cycle_start_date) <= getdate(leave_start_date) and getdate(fatal_leave_cycle_end_date) >= getdate(leave_end_date):
				return True
			else : 
				return False

def leave_allocation_exists_for_leave_cycle_year(leave_start_date, leave_end_date, employee, leave_type):
	leave_allocation_exists = frappe.db.exists("Leave Allocation", {"from_date":["<=",leave_start_date],"to_date":[">=",leave_end_date],"docstatus":1,"leave_type":leave_type,"employee":employee})
	if leave_allocation_exists:
		return True, leave_allocation_exists
	else :
		return False, None

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_annual_leave_from_contract_type(doctype, txt, searchfield, start, page_len, filters):
	annual_leave_list = frappe.db.get_all("Contract Type ST",
										   filters={"annual_leave_type": ("like", f"{txt}%")},
										   fields=["annual_leave_type"],as_list=True)
	print(annual_leave_list,"-----------annual_leave_list")
	final_annual_leave_list = tuple(set(annual_leave_list))
	return final_annual_leave_list

def is_from_time_in_shift_start_time_range(employee,date,request_time,validate=None):
	consider_default_shift = True
	shift_details = get_employee_shift(employee,get_datetime(date), consider_default_shift, None)
	if shift_details:
		shift_start_time = shift_details.start_datetime
		shift_actual_start_time = shift_details.actual_start
		permission_request_from_datetime = get_datetime(cstr(date)+" "+cstr(request_time))
		if permission_request_from_datetime >= shift_actual_start_time and permission_request_from_datetime <= shift_start_time:
			if validate==True:
				return True, shift_start_time, shift_actual_start_time
			else :
				return True, permission_request_from_datetime
		else :
			if validate==True:
				return False, shift_start_time, shift_actual_start_time
			else :
				return False, permission_request_from_datetime
		
def is_to_time_in_shift_end_time_range(employee,date,request_time,shift_type,contract_type,validate=None):
	consider_default_shift = True
	shift_details = get_employee_shift(employee,get_datetime(date), consider_default_shift, None)
	if shift_details:
		working_hours_based_on_contract_type = frappe.db.get_value("Contract Type ST",contract_type,"total_hours_per_day")
		if working_hours_based_on_contract_type:
			shift_end_time = add_to_date(shift_details.start_datetime,hours=working_hours_based_on_contract_type)
			grace_minutes_to_early_exit = frappe.db.get_single_value("Stats Settings ST","shift_early_exit_allowed_mins") or 0
			if grace_minutes_to_early_exit:
				shift_early_end_time = get_datetime(add_to_date(shift_end_time, minutes=-grace_minutes_to_early_exit))
				permission_request_to_datetime = get_datetime(cstr(date)+" "+cstr(request_time))
				if permission_request_to_datetime >= shift_early_end_time and permission_request_to_datetime <= shift_end_time:
					if validate==True:
						return True, shift_end_time, shift_early_end_time
					else :
						return True, permission_request_to_datetime
				else :
					if validate==True:
						return False, shift_end_time, shift_early_end_time
					else :
						return False, permission_request_to_datetime
			else :
				frappe.throw(_("Please Set Early Eixt minutes in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))

def create_employee_checkin(employee, shift, attendance_type, time, doctype, docname):
	employee_checkin_doc = frappe.new_doc("Employee Checkin")
	employee_checkin_doc.employee = employee
	employee_checkin_doc.shift = shift
	employee_checkin_doc.log_type = attendance_type
	employee_checkin_doc.time = get_datetime(time)
	employee_checkin_doc.custom_reference_doctype = doctype
	employee_checkin_doc.custom_reference_docname = docname
	employee_checkin_doc.custom_created_by_system = 1
	employee_checkin_doc.custom_code_remarks = "Time is based on Employee Permission Request"
	employee_checkin_doc.save(ignore_permissions=True)
	frappe.msgprint(_("Employee Checkin is created <b>{0}</b>").format(get_link_to_form("Employee Checkin",employee_checkin_doc.name)),alert=True)

def validate_deputy_employee_not_apply_for_same_dates(from_date, to_date, deputy_employee):

	deputy_employee_name = frappe.db.get_value("Employee",deputy_employee,"employee_name")
	leave_data = frappe.db.sql(
		"""
		select
			name, leave_type, posting_date, from_date, to_date, total_leave_days, half_day_date
		from `tabLeave Application`
		where employee = %(employee)s and docstatus < 2 and status in ('Open', 'Approved')
		and to_date >= %(from_date)s and from_date <= %(to_date)s
		""",
		{
			"employee": deputy_employee,
			"from_date": from_date,
			"to_date": to_date,
		},
		as_dict=1,
	)
	if len(leave_data) > 0:
		for d in leave_data:
			frappe.throw(
						_("Employee <b>{0}({1})</b> has already applied leave for <b>{2}</b> between {3} and {4}").format(
						deputy_employee, deputy_employee_name, d["leave_type"], formatdate(d["from_date"]), formatdate(d["to_date"]))
					)
	else:
		frappe.msgprint(_("Deputy Employee is not apply for leave in these dates"),indicator="green",alert=True)


def set_date_in_hijri(gregorian_date):
	# https://hijri-converter.readthedocs.io/en/stable/usage.html
	enable_hijri_date = frappe.db.get_single_value('Stats Settings ST', 'enable_hijri_date')
	if enable_hijri_date == 1:
		gregorian_splits=cstr(gregorian_date).split('-')
		year_split=cint(gregorian_splits[0])
		month_split=cint(gregorian_splits[1])
		day_split=cint(gregorian_splits[2])
		conevert_to_hijri= Gregorian(year_split,month_split,day_split).to_hijri()
		hijri_date=conevert_to_hijri.isoformat()
		return hijri_date