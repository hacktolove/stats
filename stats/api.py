import frappe
from frappe import _
from frappe.utils import (add_to_date,get_datetime,today,date_diff, add_days,get_first_day, get_last_day,
						  getdate,nowdate,format_duration,cint,format_date,
						  get_link_to_form,flt,add_years,time_diff_in_hours,
						  now,rounded,flt,get_time,time_diff_in_seconds, cstr)
from dateutil import relativedelta
from frappe.model.mapper import get_mapped_doc
import erpnext
from hijridate import Hijri, Gregorian
from erpnext.setup.doctype.employee.employee import is_holiday
from hrms.hr.doctype.shift_assignment.shift_assignment import get_employee_shift
from stats.hr_utils import validate_deputy_employee_not_apply_for_same_dates

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_main_department(doctype, txt, searchfield, start, page_len, filters):
		
		department_list = frappe.get_all("Department", filters={"is_group":0, "parent_department": ("like", f"{txt}%")}, fields=["distinct parent_department"], as_list=1)
		unique = tuple(set(department_list))
		# print(unique, '----------ab')
		return unique

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_descendant_departments(doctype, txt, searchfield, start, page_len, filters):
	main_department = filters.get('main_department')
	from frappe.utils.nestedset import NestedSet, get_ancestors_of, get_descendants_of
	descendants = get_descendants_of('Department', main_department)

	if txt:
		desc = []
		for d in descendants:
			if d.find(txt) != -1:
				desc.append(d)
		descendants = desc 

	descendants_tuple = tuple((i,) for i in descendants)
	
	return descendants_tuple


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_main_job_family(doctype, txt, searchfield, start, page_len, filters):
		
		job_family_list = frappe.get_all("Job Family ST", filters={"is_group":0}, fields=["parent_job_family_st"], as_list=1)
		unique = tuple(set(job_family_list))

		return unique

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_deputy_employee_list(doctype, txt, searchfield, start, page_len, filters):
	employee = filters.get("employee")
	is_manager = frappe.db.get_value("Employee",employee,"custom_is_manager")
	if is_manager == 1:
		is_supervisor = frappe.db.get_value("Employee",employee,"custom_supervisor_type") == "Supervisor"
		if is_supervisor:
			deputy_employee_list = frappe.db.get_all("Employee",
													filters=[
														["name", "like", f"{txt}%"],
														["name", "!=", employee],
														["custom_supervisor_type", "=", "Supervisor"],
														["custom_is_manager", "=", 1]
													],
													fields=["name","employee_name","user_id"],as_list=1)
		else:
			deputy_employee_list = frappe.db.get_all("Employee",
													filters={"reports_to":employee,"name": ("like", f"{txt}%")},
													fields=["name","employee_name","user_id"],as_list=1)
	if is_manager == 0:
		sub_department = frappe.db.get_value("Employee",employee,"custom_sub_department")
		if sub_department:
				deputy_employee_list = frappe.db.get_all("Employee",
														filters={"custom_sub_department":sub_department,"name": ("like", f"{txt}%")},
														fields=["name","employee_name","user_id"],as_list=1)
			
	return deputy_employee_list

@frappe.whitelist()
def get_supplier_contact(supplier):
	supplier_contact = frappe.db.sql(
		"""
		SELECT
			contact.name
		FROM
			`tabDynamic Link` AS link
		JOIN
			`tabContact` AS contact
		ON
			contact.name=link.parent
		WHERE
			link.link_doctype='Supplier'
			and link.link_name=%s		
		ORDER BY
			contact.creation desc
		limit 1
		""",supplier,as_dict=1,debug=1)	
	if len(supplier_contact) == 0 :
		frappe.msgprint(_("No contact found for supplier: {0}").format(supplier))
		return
	return supplier_contact[0].name

def set_todo_status_in_onboarding_procedures(self, method):
	if not self.is_new() and self.reference_type == "Employee Onboarding ST":
		doc = frappe.get_doc('Onboarding Procedures ST', {'todo':self.name})
		if doc:
			if self.status == "Closed":
				frappe.db.set_value('Onboarding Procedures ST', doc.name, 'date_of_completion', self.date)
				frappe.db.set_value('Onboarding Procedures ST', doc.name, 'status', self.status)
				frappe.msgprint(_("Update Status and Date of Completion in {0} 's Onboarding Procedures Row No. {1}")
					.format(doc.parent, doc.idx), alert=1)
			else:
				frappe.db.set_value('Onboarding Procedures ST', doc.name, 'status', self.status)
				frappe.db.set_value('Onboarding Procedures ST', doc.name, 'date_of_completion', None)
				frappe.msgprint(_("Update Status in {0} 's Onboarding Procedures Row No. {1}")
					.format(doc.parent, doc.idx), alert=1)
				
def set_employee_company_email(self, method):
	if self.reference_type == "Employee Onboarding ST":
		if self.custom_create_company_email == 1 and self.custom_company_email and self.status == "Open" and self.reference_name:
			job_offer_reference = frappe.db.get_value("Employee Onboarding ST", self.reference_name, 'job_offer_reference')
			if job_offer_reference:
				employee_list = frappe.db.get_all('Employee', filters={'custom_job_offer_reference': job_offer_reference}, fields=["name"])

				# check employee created for job offer or not
				if len(employee_list) < 1 :
					frappe.throw(_("No Employee Found For Job Offer {0}").format(get_link_to_form('Job Offer ST', job_offer_reference)))

				employee = frappe.get_doc("Employee", {'custom_job_offer_reference': job_offer_reference})

				if employee.company_email and employee.company_email == self.custom_company_email:
					if (employee.attendance_device_id and employee.attendance_device_id != employee.company_email) or not employee.attendance_device_id:
						employee.attendance_device_id = employee.company_email
						employee.save(ignore_permissions=True)
					print("Same Company Email ID")
				else:
					employee.company_email = self.custom_company_email
					employee.attendance_device_id = employee.company_email
					employee.save(ignore_permissions=True)
				return employee.name

def create_new_user_using_company_email_in_employee(self, method):
	employee = set_employee_company_email(self, method)
	if employee:
		emp = frappe.get_doc('Employee', employee)
		user_exist = frappe.db.exists("User", emp.company_email)

		if user_exist:
			frappe.msgprint(_("User {0} is already exists").format(emp.company_email), alert=1)
			return
		if emp.company_email and not emp.user_id:


			new_user = frappe.new_doc("User")
			new_user.update({
				"email": emp.company_email,
				"enabled": 1,
				"first_name": emp.employee_name,
				"send_welcome_email": 0
			})

			new_user.insert(ignore_permissions=True)

			if emp.designation:
				roles = frappe.db.sql_list("""select role from `tabDesignation Roles ST`
					where parent='{0}'""".format(emp.designation))
				if roles:
					new_user.add_roles(*roles)

				module_profile = frappe.db.get_value("Designation", emp.designation, 'custom_module_profile')

				if module_profile:
					new_user.module_profile = module_profile
					
				else:
					block_modules = frappe.get_all(
						"Module Def",
						fields=["name as module"]
					)
					if block_modules:
						new_user.set("block_modules", block_modules)
				
				new_user.save(ignore_permissions=True)

			emp.user_id = new_user.name
			emp.create_user_permission = 1
			emp.save(ignore_permissions=True)

			frappe.msgprint(_("User {0} is created."
				.format(get_link_to_form('User', new_user.name))), alert=True)

		else:
			frappe.msgprint(_("Employee {0} 's User ID {1} is already set.").format(emp.name, emp.user_id), alert=1)


def calculate_years_of_experience(self, method):
	diff = relativedelta.relativedelta(getdate(nowdate()), getdate(self.date_of_joining))

	years = diff.years
	months = diff.months
	days = diff.days

	if self.custom_previous_years_of_experience:
		previous_years = years + self.custom_previous_years_of_experience

		self.custom_current_years_of_experience = str(years) + " years " + str(months) + " months " + str(days) + " days"
		self.custom_total_years_of_experience = str(previous_years) + " years " + str(months) + " months " + str(days) + " days"

def set_employee_in_man_power_planning_for_job_no(self, method):
	old_doc = self.get_doc_before_save()

	if self.custom_job_no and not self.is_new() and self.status != "Left":
		job_no = frappe.get_doc("MP Jobs Details ST",{"job_no":self.custom_job_no})
		if not job_no.employee_no:
			frappe.db.set_value(job_no.doctype, job_no.name, "employee_no", self.name)
			man_power_planing = frappe.get_doc("Man Power Planning ST", job_no.parent)
			man_power_planing.save(ignore_permissions=True)
			self.add_comment('Comment', 'Job No {0} is Filled.'.format(self.custom_job_no))
			frappe.msgprint(_("set Employee {0} in Job No {1}").format(self.name, self.custom_job_no), alert=True)

	#### if job no is removed or employee status left
	elif (not self.custom_job_no and old_doc.custom_job_no and not self.is_new()) or (self.status == "Left" and self.custom_job_no not in [None, ""]):
		job_no = frappe.get_doc("MP Jobs Details ST",{"job_no":old_doc.custom_job_no or self.custom_job_no})
		if job_no.employee_no:
			frappe.db.set_value(job_no.doctype, job_no.name, "employee_no", '')
			frappe.db.set_value(job_no.doctype, job_no.name, "position_status", 'Vacant')
			frappe.db.set_value(job_no.doctype, job_no.name, "supply_name", '')

			if self.status == "Left":
				self.custom_job_no = ""
				self.add_comment('Comment', 'Job No {0} is Vacant Because Employee is Left.'.format(old_doc.custom_job_no))
			else:
				self.add_comment('Comment', 'Job No {0} is Vacant.'.format(old_doc.custom_job_no))

			man_power_planing = frappe.get_doc("Man Power Planning ST", job_no.parent)
			man_power_planing.save(ignore_permissions=True)
			frappe.msgprint(_("Job No {0} is Vacant.").format(old_doc.custom_job_no), alert=True)


def convert_gregorian_dob_in_hijri_dob(self, method):
	enable_hijri_date = frappe.db.get_single_value('Stats Settings ST', 'enable_hijri_date')
	if enable_hijri_date == 1:
		print(self.date_of_birth, "-----self.date_of_birth", type(self.date_of_birth), '==type')
		gregorian_splits=cstr(self.date_of_birth).split('-')
		year_split=cint(gregorian_splits[0])
		month_split=cint(gregorian_splits[1])
		day_split=cint(gregorian_splits[2])
		dob_hijri= Gregorian(year_split,month_split,day_split).to_hijri()
		dobj_hijri_iso=dob_hijri.isoformat()
		dobj_hijri_tuple=dob_hijri.datetuple()
		readable_hijri= dob_hijri.month_name()+" "+cstr(dobj_hijri_tuple[2])+","+cstr(dobj_hijri_tuple[0])+" "+dob_hijri.notation()
		hijri_date = dobj_hijri_iso
		final_hijri_date = (hijri_date[:140]) if len(hijri_date) > 140 else hijri_date
		self.custom_hijri_birth_date = final_hijri_date
		# return final_hijri_date
 
@frappe.whitelist()
def set_years_of_experience_at_start_of_every_month():
	employees=frappe.db.get_list('Employee', filters={'status': ['=', 'Active']})
	for employee in employees:
		emp_doc=frappe.get_doc("Employee",employee)
		diff = relativedelta.relativedelta(getdate(nowdate()), getdate(emp_doc.date_of_joining))

		years = diff.years
		months = diff.months
		days = diff.days

		print("in employee")

		if emp_doc.custom_previous_years_of_experience:
			print("yes")
			previous_years = years + emp_doc.custom_previous_years_of_experience
			emp_doc.custom_current_years_of_experience = str(years) + " years " + str(months) + " months " + str(days) + " days"
			emp_doc.custom_total_years_of_experience = str(previous_years) + " years " + str(months) + " months " + str(days) + " days"
			emp_doc.add_comment("Comment", text='Employee experience added till {0}'.format(nowdate()))
			print("added")
			emp_doc.save(ignore_permissions=True)

@frappe.whitelist()
def fetch_employee_per_diem_amount(employee,no_of_days,trip_type):
	employee_grade = frappe.db.get_value("Employee",employee,"grade")
	if employee_grade:
		if trip_type:
			if trip_type == "Internal":
				employee_per_diem_amount = frappe.db.get_value("Employee Grade",employee_grade,"custom_per_diem")
				if employee_per_diem_amount == 0:
					frappe.throw(_("Please set Internal per diem amount for employee in employee grade {0}").format(get_link_to_form("Employee Grade",employee_grade)))
			elif trip_type == "External":
				employee_per_diem_amount = frappe.db.get_value("Employee Grade",employee_grade,"custom_external_per_diem")
				if employee_per_diem_amount == 0:
					frappe.throw(_("Please set External per diem amount for employee in employee grade {0}").format(get_link_to_form("Employee Grade",employee_grade)))
		total_employee_amount_for_trip = employee_per_diem_amount * cint(no_of_days)
		per_diem_amount = employee_per_diem_amount
		return total_employee_amount_for_trip, per_diem_amount
	else:
		frappe.throw(_("Please set Grade In Employee Profile"))


@frappe.whitelist()
def set_no_of_business_trip_days_available_at_start_of_every_year():
	employees=frappe.db.get_list('Employee', filters={'status': ['=', 'Active']})
	for employee in employees:
		emp_doc=frappe.get_doc("Employee",employee)
		custom_contract_type=emp_doc.custom_contract_type
		no_of_allowed_business_trip_days = frappe.db.get_value('Contract Type ST', custom_contract_type, 'no_of_allowed_business_trip_days')
		emp_doc.custom_no_of_business_trip_days_remaining=no_of_allowed_business_trip_days
		emp_doc.add_comment("Comment", text='No of business trip days are set to {0} on {1} by system.'.format(no_of_allowed_business_trip_days,nowdate()))
		emp_doc.save(ignore_permissions=True)

@frappe.whitelist()
def check_leave_is_not_in_business_days(self,method):
		business_trip_request_details=	frappe.db.sql(
					"""
					select
						name
					from `tabBusiness Trip Request ST`
					where employee_no = %(employee)s and docstatus < 2 and status in ('Pending', 'Approved')
					and (
					( business_trip_start_date <= %(from_date)s and business_trip_end_date >= %(from_date)s )
					or ( business_trip_start_date >= %(from_date)s and business_trip_end_date <= %(to_date)s )
					or ( business_trip_start_date <= %(to_date)s and business_trip_end_date >= %(to_date)s )
					)
					""",
					{
						"employee": self.employee,
						"from_date": self.from_date,
						"to_date": self.to_date,
					},
					as_dict=1
				)
		print('business_trip_request_details',business_trip_request_details)
		if len(business_trip_request_details)>0:
			business_trip_names=",".join(i.name for i in business_trip_request_details)
			frappe.throw(_("You have business trip <b>{0}</b> during your leave application days. It is not allowed.").format(business_trip_names))

def validate_leave_types(self, method):
	if not self.custom_leave_request_reference and self.leave_type:
		custom_once_in_company_life, custom_based_on_leave_request = frappe.db.get_value("Leave Type", self.leave_type, ["custom_once_in_company_life","custom_based_on_leave_request"])
		if custom_once_in_company_life == 1 or custom_based_on_leave_request == 1:
			frappe.throw(_("You Cann't Apply for {0} Leave Type. Go To Leave Request Doctype for this leave type").format(self.leave_type))		
				
def create_budget(cost_center, fiscal_year, budget_expense_account, net_balance):
	print('create_budget')

	new_budget = frappe.new_doc('Budget')
	new_budget.cost_center = cost_center
	new_budget.fiscal_year = fiscal_year
	row = new_budget.append('accounts',{})
	row.account = budget_expense_account
	row.budget_amount = net_balance

	new_budget.submit()
	frappe.msgprint(_("Budget {0} is created."
		.format(get_link_to_form('Budget', new_budget.name))), alert=True)
	print(new_budget.name ,'------new_budget')

	return new_budget.name

@frappe.whitelist()
def set_scholarship_status_closed():
	open_scholarship_list = frappe.db.get_all("Scholarship ST",
										   filters = {"docstatus":1,"status":"Open"},
										   fields=["name","apply_end_date","status"])
	for scholarship in open_scholarship_list:
		if scholarship.apply_end_date == getdate(nowdate()):
			scholarship_doc = frappe.get_doc("Scholarship ST",scholarship.name)
			scholarship_doc.status = "Closed"
			scholarship_doc.add_comment("Comment", text='Scholarship status is Closed on {0} by system.'.format(nowdate()))
			scholarship_doc.save(ignore_permissions = True)

def create_salary_component(name,abbreviation,type):
	salary_component_doc = frappe.new_doc("Salary Component")
	salary_component_doc.salary_component = name
	salary_component_doc.salary_component_abbr = abbreviation
	salary_component_doc.type = "Deduction"
	salary_component_doc.run_method('set_missing_values')
	salary_component_doc.save(ignore_permissions=True)

def check_monthly_salary_component_offer_term(self,method):
    if self.get("custom_is_monthly_salary_component") == 1:
        offer_term_list = frappe.db.get_all("Offer Term",
                                      filters={"custom_is_monthly_salary_component":1, "name": ["!=", self.name]},
                                      fields=["name"])
        if len(offer_term_list)>0:
                frappe.throw(_("Offer Term <b>'{0}'</b> is already set as Monthly Salary Component".format(offer_term_list[0].name)))

def create_salary_structure_assignment(self, method):
	if (self.custom_employee_contract_ref or self.custom_employee_no) and self.custom_type_of_creation != "GOSI":
		total_monthly_salary = 0
		if len(self.earnings)>0:
			for ear in self.earnings:
				total_monthly_salary = total_monthly_salary + ear.amount

		# amount = frappe.db.get_value("Employee Contract ST", self.custom_employee_contract_ref, "total_monthly_salary")
		assignment = frappe.new_doc("Salary Structure Assignment")
		assignment.employee = self.custom_employee_no
		assignment.salary_structure = self.name
		assignment.from_date = self.custom_contract_start_date
		assignment.base = total_monthly_salary

		assignment.save(ignore_permissions=True)
		frappe.msgprint(_("Salary Structure Assignment {0} created." .format(get_link_to_form('Salary Structure Assignment', assignment.name))), alert=True)
		assignment.submit()

def get_monthly_salary_from_job_offer(job_offer):
	doc = frappe.get_doc("Job Offer ST", job_offer)

	if doc:
		monthly_salary = 0
		if len(doc.offer_details) > 0:
			for offer in doc.offer_details:
				monthly_salary_component = frappe.db.get_value('Offer Term', offer.offer_term, 'custom_is_monthly_salary_component')
				if monthly_salary_component == 1:
					monthly_salary = offer.value

	return monthly_salary

def get_base_amount_from_salary_structure_assignment(employee):
	base = frappe.db.get_value("Salary Structure Assignment", {"employee":employee, "docstatus":1}, 'base')
	if base == None:
		frappe.throw(_("No Base Amount Found"))
	else:
		return base

def validate_weight_and_set_degree_based_on_weight(self, method):
	validate_weight(self.custom_basic_competencies,competencies_type="Basic Competencies")
	validate_weight(self.custom_technical_competencies,competencies_type="Technical Competencies")
	validate_weight(self.custom_leadership,competencies_type="Leadership")

def set_degree_based_on_weight(details):
	if len(details)>0:
		for row in details:
			if row.weight and row.target_degree:
					row.degree_based_on_weight = flt((row.weight * row.target_degree) / 100,2)

def validate_weight(details, competencies_type=None):
	if len(details)>0:
		total_weight = 0
		for row in details:
			if row.weight:
				total_weight = total_weight + row.weight
			else:
				frappe.throw(_("Row #{0}: Weight cannot be 0 in {1}".format(row.idx, competencies_type)))
		if total_weight != 100:
			frappe.throw(_("Total of weight must be 100 in {0}".format(competencies_type)))

def calculate_actual_degree_based_on_weight(details):
	if len(details)>0:
		for row in details:
			if row.actual_degree and row.weight:
				row.actual_degree_based_on_weight = flt((row.actual_degree * row.weight) / 100, 2)

@frappe.whitelist()
def create_employee_evaluation_yearly_and_half_yearly():
	stats_settings_doc = frappe.get_doc("Stats Settings ST")
	today = getdate(nowdate())
	# today = getdate("2026-12-31")
	print(today,"today",type(today),"stats_settings_doc",stats_settings_doc.annual_creation_date,type(getdate(stats_settings_doc.annual_creation_date)))
	if today == getdate(stats_settings_doc.annual_creation_date):
		all_active_employee_list = frappe.db.get_all("Employee",filters={"status":"Active","custom_test_period_completed":"Yes"},fields=["name"])

		if len(all_active_employee_list)>0:
			for employee in all_active_employee_list:
				employee_doc = frappe.get_doc("Employee",employee.name)
				employee_evaluation_doc = frappe.new_doc("Employee Evaluation ST")
				if today == getdate(stats_settings_doc.annual_creation_date):
					employee_evaluation_doc.employee_no = employee.name
					employee_evaluation_doc.creation_date = stats_settings_doc.annual_creation_date
					employee_evaluation_doc.evaluation_type = "Yearly"
					employee_evaluation_doc.evaluation_from = stats_settings_doc.annual_evaluation_from
					employee_evaluation_doc.evaluation_to = stats_settings_doc.annual_evaluation_to

				elif today == getdate(stats_settings_doc.half_yearly_creation_date):
					employee_evaluation_doc = frappe.new_doc("Employee Evaluation ST")
					employee_evaluation_doc.employee_no = employee.name
					employee_evaluation_doc.creation_date = stats_settings_doc.half_yearly_creation_date
					employee_evaluation_doc.evaluation_type = "Half Yearly"
					employee_evaluation_doc.evaluation_from = stats_settings_doc.half_yearly_evaluation_from
					employee_evaluation_doc.evaluation_to = stats_settings_doc.half_yearly_evaluation_to
				
				employee_personal_goal = frappe.db.get_all("Employee Personal Goals ST",
												filters={"employee_no":employee.name,"docstatus":1},
												fields=["name"])
				if len(employee_personal_goal)>0:
					employee_personal_goal_doc = frappe.get_doc("Employee Personal Goals ST",employee_personal_goal[0].name)
					if len(employee_personal_goal_doc.personal_goals)>0:
						for row in employee_personal_goal_doc.personal_goals:
							personal_goal = employee_evaluation_doc.append("employee_personal_goals",{})
							personal_goal.goals = row.goals
							personal_goal.weight = row.weight
							personal_goal.target_degree = row.target_degree

				if employee_doc.grade:
					evaluation_template = frappe.db.get_all("Employee Evaluation Template ST",
												filters={"grade":employee_doc.grade},
												fields=["name"])
					if len(evaluation_template)>0:
						evaluation_template_doc = frappe.get_doc("Employee Evaluation Template ST",evaluation_template[0].name)
						if len(evaluation_template_doc.job_goals)>0:
							for row in evaluation_template_doc.job_goals:
								job_goal = employee_evaluation_doc.append("employee_job_goals",{})
								job_goal.goals = row.goals
								job_goal.weight = row.weight
								job_goal.uom = row.uom
								job_goal.target_degree = row.target_degree

				if employee_doc.designation:
					designation_doc = frappe.get_doc("Designation",employee_doc.designation)
					if len(designation_doc.custom_management_skills)>0:
						for row in designation_doc.custom_management_skills:
							management_skill = employee_evaluation_doc.append("employee_management_skills",{})
							management_skill.skill = row.skill
							management_skill.skill_description = row.skill_description
							management_skill.weight = row.weight
							management_skill.target_degree = row.target_degree

				employee_evaluation_doc.save(ignore_permissions=True)
				employee_evaluation_doc.add_comment("Comment",text="Created by system on {0}".format(nowdate()))

			if today == getdate(stats_settings_doc.annual_creation_date):
				next_yearly_evaluation_date = add_years(stats_settings_doc.annual_creation_date, 1)
				next_yearly_evaluation_from_date = add_years(stats_settings_doc.annual_evaluation_from, 1)
				next_yearly_evaluation_to_date = add_years(stats_settings_doc.annual_evaluation_to, 1)

				print(next_yearly_evaluation_date,"next_yearly_evaluation_date","----",next_yearly_evaluation_from_date,'next_yearly_evaluation_from_date',"----",next_yearly_evaluation_to_date,"next_yearly_evaluation_to_date")
				stats_settings_doc.annual_creation_date = next_yearly_evaluation_date
				stats_settings_doc.annual_evaluation_from = next_yearly_evaluation_from_date
				stats_settings_doc.annual_evaluation_to = next_yearly_evaluation_to_date
				stats_settings_doc.add_comment("Comment",text="Annual Evaluation Default Dates are updated on {0}".format(nowdate()))
				stats_settings_doc.save(ignore_permissions=True)
				
			elif today == getdate(stats_settings_doc.half_yearly_creation_date):
				next_half_yearly_evaluation_date = add_years(stats_settings_doc.half_yearly_creation_date, 1)
				next_half_yearly_evaluation_from_date = add_years(stats_settings_doc.half_yearly_evaluation_from, 1)
				next_half_yearly_evaluation_to_date = add_years(stats_settings_doc.half_yearly_evaluation_to, 1)

				print(next_half_yearly_evaluation_date,"next_half_yearly_evaluation_date","----",next_half_yearly_evaluation_from_date,'next_half_yearly_evaluation_from_date',"----",next_half_yearly_evaluation_to_date,"next_yearly_evaluation_to_date")
				stats_settings_doc.half_yearly_creation_date = next_half_yearly_evaluation_date
				stats_settings_doc.half_yearly_evaluation_from = next_half_yearly_evaluation_from_date
				stats_settings_doc.half_yearly_evaluation_to = next_half_yearly_evaluation_to_date
				stats_settings_doc.add_comment("Comment",text="Half-Yearly Evaluation Default Dates are updated on {0}".format(nowdate()))
				stats_settings_doc.save(ignore_permissions=True)

@frappe.whitelist()
def create_employee_evaluation_based_on_employee_contract():
	today = getdate(nowdate())
	# today = getdate("2024-12-26")
	employee_contract_list = frappe.db.get_all("Employee Contract ST",
											filters={"docstatus":1},
											or_filters={"test_period_end_date":today,"end_of_new_test_period":today},
											fields=["name"])
	# default_template_for_test_period = frappe.db.get_single_value("Stats Settings ST","default_evaluation_template_for_test_period")
	if len(employee_contract_list)>0:
		for contract in employee_contract_list:
			print(contract,"--")
			employee_contract_doc = frappe.get_doc("Employee Contract ST",contract.name)
			if employee_contract_doc.end_of_new_test_period or employee_contract_doc.test_period_end_date:
				employee_evaluation_doc = frappe.new_doc("Employee Evaluation ST")
				employee_evaluation_doc.employee_no = employee_contract_doc.employee_no
				employee_evaluation_doc.creation_date = today
				employee_evaluation_doc.evaluation_type = "Test Period"
				employee_evaluation_doc.employee_contract_reference = employee_contract_doc.name

				if employee_contract_doc.end_of_new_test_period == today:
					employee_evaluation_doc.evaluation_from = employee_contract_doc.test_period_end_date
					employee_evaluation_doc.evaluation_to = employee_contract_doc.end_of_new_test_period

				elif employee_contract_doc.test_period_end_date == today:
					employee_evaluation_doc.evaluation_from = employee_contract_doc.contract_start_date
					employee_evaluation_doc.evaluation_to = employee_contract_doc.test_period_end_date
				
				employee_designation = frappe.db.get_value("Employee",employee_contract_doc.employee_no,"designation")

				if employee_designation:
					designation_doc = frappe.get_doc("Designation",employee_designation)
					if len(designation_doc.custom_basic_competencies)>0:
						for row in designation_doc.custom_basic_competencies:
							basic_skill = employee_evaluation_doc.append("basic_competencies",{})
							basic_skill.competencies_name = row.competencies_name
							basic_skill.description = row.description
							basic_skill.weight = row.weight
							basic_skill.degree_out_of_5 = row.degree_out_of_5
					
					if len(designation_doc.custom_technical_competencies)>0:
						for row in designation_doc.custom_technical_competencies:
							technical_skill = employee_evaluation_doc.append("technical_competencies",{})
							technical_skill.competencies_name = row.competencies_name
							technical_skill.description = row.description
							technical_skill.weight = row.weight
							technical_skill.degree_out_of_5 = row.degree_out_of_5

					if len(designation_doc.custom_leadership)>0:
						for row in designation_doc.custom_leadership:
							leadership_skill = employee_evaluation_doc.append("leadership",{})
							leadership_skill.competencies_name = row.competencies_name
							leadership_skill.description = row.description
							leadership_skill.weight = row.weight
							leadership_skill.degree_out_of_5 = row.degree_out_of_5

				employee_evaluation_doc.save(ignore_permissions=True)
				employee_evaluation_doc.add_comment("Comment",text="Created by system on {0}".format(nowdate()))

def calculate_extra_working_hours(self,method):

	actual_working_minutes = self.custom_working_minutes_per_day
	employee_working_hours = self.working_hours

	# rounded_employee_working_hours = rounded(employee_working_hours - actual_working_hours, 0)
	if employee_working_hours and (employee_working_hours > 0):
		employee_working_minutes = employee_working_hours * 60
		self.custom_actual_working_minutes = employee_working_minutes
		if self.custom_net_working_minutes==None or self.custom_net_working_minutes == 0:
			print("0 net hours ------------------------------")
			self.custom_net_working_minutes = self.custom_actual_working_minutes

		# if employee_working_minutes > actual_working_minutes:
		total_extra_min = employee_working_minutes - actual_working_minutes
		self.custom_extra_minutes = total_extra_min

	if not self.custom_attendance_type:
		if self.status:
			self.custom_attendance_type = self.status

def set_custom_attendance_type(self,method):
	print("==="*10)
	print(self.name,self.employee)
	# required to do as on leave application, attendance is created by passing the validate hook
	print(self.custom_working_minutes_per_day,"==========",self.custom_net_working_minutes)
	employee_contract_type = frappe.db.get_value("Employee",self.employee,"custom_contract_type")
	if employee_contract_type:
		if self.custom_net_working_minutes==None or self.custom_net_working_minutes == 0:
			frappe.db.set_value('Attendance', self.name, 'custom_net_working_minutes', self.custom_working_minutes_per_day)
	if not self.custom_attendance_type:
		if self.status:
			frappe.db.set_value('Attendance', self.name, 'custom_attendance_type', self.status)
			if self.leave_type:
				is_lwp = frappe.db.get_value('Leave Type', self.leave_type, 'is_lwp')
				if is_lwp==1:
					frappe.db.set_value('Attendance', self.name, 'custom_attendance_type', 'On LWP')	

def validate_duplicate_record_for_employee_checkin(self):
		# employee_checkin = frappe.db.get_all("Employee Checkin",
		# 							   filters={"employee":self.employee,"log_type":self.log_type,"time":self.time},
		# 							   fields=["name","time"])
		employee_checkin = frappe.db.exists("Employee Checkin",{"employee":self.employee,"log_type":self.log_type,"time":self.time})
		
		print(employee_checkin,"-----")
		# if len(employee_checkin)>0:
		if employee_checkin != None and employee_checkin != self.name:
			print("Done")
			frappe.throw(_("This employee already has a employee checkin with the same date and attendance type <br><b>{0}</b>").format(get_link_to_form("Employee Checkin",ele.name)))

def set_last_sync_of_checkin_in_all_shift_type():
	shift_list = frappe.get_all("Shift Type", filters={"enable_auto_attendance": "1"}, pluck="name")
	for shift in shift_list:
		shift_type_doc = frappe.get_doc("Shift Type",shift)
		shift_type_doc.last_sync_of_checkin = now()
		shift_type_doc.add_comment("Comment",text="Last Sync of Checkin is updated by system on {0}".format(now()))
		shift_type_doc.save(ignore_permissions=True)

def set_last_sync_of_checkin_on_save_of_employee_checkin(self,method):
	if not (self.skip_auto_attendance or not self.shift):
		print("IN FUNC ----------------------------")
		latest_checkin = frappe.get_last_doc("Employee Checkin", filters={"shift": self.shift}, order_by="time desc")
		current_last_sync_of_checkin_in_shift = frappe.db.get_value("Shift Type", self.shift, "last_sync_of_checkin")
		print(latest_checkin.time,"latest_checkin.time-------",type(latest_checkin.time),current_last_sync_of_checkin_in_shift,"current_last_sync_of_checkin_in_shift",type(current_last_sync_of_checkin_in_shift))
		if current_last_sync_of_checkin_in_shift == None:
			frappe.db.set_value("Shift Type", self.shift, "last_sync_of_checkin", latest_checkin.time)
		if current_last_sync_of_checkin_in_shift and latest_checkin.time > current_last_sync_of_checkin_in_shift:
			print("Valid -----")
			frappe.db.set_value("Shift Type", self.shift, "last_sync_of_checkin", latest_checkin.time)

	
@frappe.whitelist()
def create_payment_journal_entry_from_payment_procedure(doc,debit_account,credit_account,amount,je_date=None,party_type=None,party_name=None):
	if je_date == None:
		je_date = today()

	payment_je_doc = frappe.new_doc("Journal Entry")
	payment_je_doc.voucher_type = "Journal Entry"
	payment_je_doc.posting_date = je_date
	payment_je_doc.custom_payment_procedure_reference = doc.name

	accounts = []

	company = erpnext.get_default_company()
	company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")

	accounts_row = {
		"account":debit_account,
		"cost_center":company_default_cost_center,
		"debit_in_account_currency":amount,
	}

	account_type = frappe.get_cached_value("Account",debit_account, "account_type")
	if account_type in ["Receivable", "Payable"]:
		accounts_row["party_type"]=party_type
		accounts_row["party"]=party_name

	accounts.append(accounts_row)
	accounts_row_2 = {
		"account":credit_account,
		"cost_center":company_default_cost_center,
		"credit_in_account_currency":amount,
	}
	account_type = frappe.get_cached_value("Account",credit_account, "account_type")
	if account_type in ["Receivable", "Payable"]:
		accounts_row_2["party_type"]=party_type
		accounts_row_2["party"]=party_name
	accounts.append(accounts_row_2)

	payment_je_doc.set("accounts",accounts)
	payment_je_doc.run_method('set_missing_values')
	payment_je_doc.save(ignore_permissions=True)
	payment_je_doc.submit()

	frappe.msgprint(_("Payment Journal Entry is created from Payment Procedure {0}").format(get_link_to_form("Journal Entry",payment_je_doc.name)),alert=1)


@frappe.whitelist()
def create_purchase_comittee(source_name, target_doc=None):
	doc = frappe.get_doc("Material Request", source_name)

	def set_missing_values(source, target):
		target.material_request_reference = source.name
		target.created_by = source.custom_created_by
		target.main_department = source.custom_main_department
		target.sub_department = source.custom_sub_department
		target.project_manager = source.custom_project_manager
		target.project_owner = source.custom_project_owner
		target.reference_in_eatimad = source.custom_reference_in_eatimad
		target.initial_cost = source.custom_initial_cost
		target.request_type = source.custom_request_type

	doc = get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": "Purchasing Committee ST",
				"field_map": {
					"material_request_reference": "name",
				},
			}
		},
		target_doc,
		set_missing_values,
	)
	return doc

def validate_request_classification(self, method):
	if self.custom_initial_cost:
		if self.custom_request_classification in ["General Competition","Two Level Competition"]:
			if self.custom_initial_cost <= 100000:
				frappe.throw(_("Your initial cost is less then 100000. <br>Hence You cannot select Request classification as <b>{0}</b>".format(self.custom_request_classification)))
		elif self.custom_request_classification =="Limited Competition":
			# no restriction
			pass
		else :
			if self.custom_initial_cost > 100000:
				frappe.throw(_("Your initial cost is greater then 100000. <br>Hence You cannot select Request classification as <b>{0}</b>".format(self.custom_request_classification)))

def fetch_values_from_material_request(self, method):
	if len(self.items)>0:
		for row in self.items:
			if row.material_request:
				material_request_doc = frappe.get_doc("Material Request",row.material_request)
				self.custom_request_classification = material_request_doc.custom_request_classification
				self.custom_reference_in_eatimad = material_request_doc.custom_reference_in_eatimad
				self.custom_initial_cost = material_request_doc.custom_initial_cost
				self.custom_request_type = material_request_doc.custom_request_type
				purchase_committee = frappe.db.get_all("Purchasing Committee ST",
										   filters={"material_request_reference":row.material_request},
										   fields=["name"])
				if len(purchase_committee)>0:
					self.custom_purchasing_committee_ref = purchase_committee[0].name
				break

@frappe.whitelist()
def make_leave_application_change_request(source_name, target_doc=None):
	doc = frappe.get_doc("Leave Application", source_name)

	def set_missing_values(source, target):
		target.leave_application_reference = source.name
		target.employee_no = source.employee
		target.employee_name = source.employee_name

	doc = get_mapped_doc(
		"Leave Application",
		source_name,
		{
			"Leave Application": {
				"doctype": "Leave Change Request ST",
				"field_map": {
					"leave_application_reference": "name",
				},
			}
		},
		target_doc,
		set_missing_values,
	)
	return doc

def validate_evaluation_weight(self, method):
	weight_total = self.custom_employee_personal_goal_weight + self.custom_employee_job_goal_weight + self.custom_competencies_weight
	if weight_total != 100:
		frappe.throw(_("Weight total must be 100"))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_po_budget_account(doctype, txt, searchfield, start, page_len, filters):
	po_name = filters.get("po_name")
	po_details_list = frappe.db.get_all("Purchase Order Item", parent_doctype = "Purchase Order", filters={"parent":po_name,"expense_account":("like", f"{txt}%")}, fields=["distinct expense_account"],as_list =1)
	unique = tuple(set(po_details_list))
	return unique

@frappe.whitelist()
def create_po_payment_schedule(source_name, target_doc=None):
	doc = frappe.get_doc("Purchase Order", source_name)

	def set_missing_values(source, target):
		target.po_reference = source.name

	doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		{
			"Purchase Order": {
				"doctype": "PO Payment Schedule ST",
			}
		},
		target_doc,
		set_missing_values,
	)
	return doc

@frappe.whitelist()
def create_achievement_certificate(doctype,doc):
	print(doctype,"doctype")
	pi_doc = frappe.get_doc(doctype, doc)
	certificate_doc = frappe.new_doc("Achievement Certificate ST")
	certificate_doc.reference_type = pi_doc.doctype
	certificate_doc.invoice_reference = pi_doc.name
	certificate_doc.supplier = pi_doc.supplier
	certificate_doc.project_owner = pi_doc.custom_project_owner
	certificate_doc.achievement_date = today()
	if doctype == "Purchase Order":
		total_paid_amount=0
		paid_amount_details = frappe.db.sql("""
						SELECT
							SUM(pii.amount) as total_paid_amount
						FROM
							`tabPurchase Invoice` pi
						INNER JOIN `tabPurchase Invoice Item` pii ON
							pi.name = pii.parent
						WHERE pi.docstatus=1 and pii.purchase_order='{0}' and pi.status='Paid'
						GROUP BY pii.purchase_order 
							  """.format(pi_doc.name),as_dict=1)
		if len(paid_amount_details)>0:
			total_paid_amount = paid_amount_details[0].total_paid_amount

		certificate_doc.paid_amount = total_paid_amount
		certificate_doc.pending_amount = pi_doc.grand_total-total_paid_amount
	else :
		certificate_doc.payment_amount = pi_doc.outstanding_amount
	certificate_doc.project_manager = pi_doc.custom_project_manager
	certificate_doc.contract_date = pi_doc.custom_contract_start_date
	certificate_doc.contract_period = pi_doc.custom_contract_period
	certificate_doc.run_method("set_missing_values")
	certificate_doc.save(ignore_permissions=True)
	frappe.msgprint(_("Achievement Certificate is created {0}".format(get_link_to_form("Achievement Certificate ST",certificate_doc.name))),alert=True)

	return certificate_doc.name

def set_work_from_home_days_in_attendance_request(self,method):
	if self.reason == "Work From Home":
		if getdate(self.from_date).month != getdate(self.to_date).month:
			frappe.throw(_("you cannot apply work from home for two different months"))
		work_from_home_days = 0
		request_days = date_diff(self.to_date, self.from_date) + 1
		for day in range(request_days):
			attendance_date = add_days(self.from_date, day)
			check_if_holiday = is_holiday(self.employee, attendance_date)
			if check_if_holiday == False:
				work_from_home_days = work_from_home_days + 1
		if work_from_home_days > 2:
			frappe.throw(_("You cannot apply for more than 2 days of work from home"))
		self.custom_work_from_home_days = work_from_home_days

def validate_max_allowed_wfh_per_month_and_max_allowed_employee_per_day(self,method):
	if self.reason == "Work From Home":
		month_start_date = get_first_day(self.from_date)
		month_end_date = get_last_day(self.from_date)
		request_days = date_diff(self.to_date, self.from_date) + 1
		for day in range(request_days):
			attendance_date = add_days(self.from_date, day)
			check_25_percent_employee_apply_work_from_home_per_day(attendance_date, self.custom_sub_department)
			check_more_than_2_days_work_from_home(self.employee, month_start_date, month_end_date, self.custom_work_from_home_days)

def validate_attendance_request_from_date(self, method):
	do_not_allow_past_attendance_request = frappe.db.get_single_value("Stats Settings ST", "do_not_allow_past_attendance_request")
	if getdate(self.from_date) <= getdate(nowdate()) and do_not_allow_past_attendance_request == 1:
		frappe.throw(_("Requests for attendance must be made in advance; past and current dates are not allowed."))

def check_25_percent_employee_apply_work_from_home_per_day(attendance_date, sub_department):
	allowed_employee_per_day = 0
	ratio_for_work_from_home = frappe.db.get_single_value("Stats Settings ST", "employee_allowed_for_work_from_home_per_day")
	if ratio_for_work_from_home == None or ratio_for_work_from_home == "" or ratio_for_work_from_home == 0:
		frappe.throw(_("Please set the Employee Allowed For Work From Home Per Day in {0}").format(get_link_to_form("Stats Settings ST", "Stats Settings ST")))
	employee_list = frappe.db.get_all("Employee",
								   filters={"status":"Active","custom_sub_department":sub_department},
								   fields=["count(name) as employee_count"])
	if len(employee_list)>0:
		employee_count = employee_list[0].employee_count
	if employee_count > 3:
		allowed_employee_per_day = (ratio_for_work_from_home * employee_count) // 100
		print(allowed_employee_per_day, '-------allowed_employee_per_day')
		if allowed_employee_per_day == 0:
			frappe.throw(_("You are not allowed to apply for work from home.<br><br>Sub Department : {0}<br>Employees in department : {1}<br>Employees allowed for Work From Home Per Day : {2}".format(sub_department,employee_count,cint(allowed_employee_per_day))))

		attendance_request_list = frappe.db.get_all("Attendance Request",
												filters={"custom_sub_department":sub_department,"from_date":["<=",attendance_date],"to_date":[">=",attendance_date],"docstatus":1,"reason":"Work From Home"},
												fields=["name"])
		if len(attendance_request_list) >= allowed_employee_per_day:
			frappe.throw(_("You cannot apply for work from home on {0} as {1} employee are already applied<br><br>Sub Department : {2}<br>Employees in department : {3}<br>Employees allowed for Work From Home Per Day : {4}").format(format_date(attendance_date),cint(allowed_employee_per_day),sub_department,employee_count,cint(allowed_employee_per_day)))

def check_more_than_2_days_work_from_home(employee, month_start, month_end, work_from_home_days):
	allowed_work_from_home_per_month = frappe.db.get_single_value("Stats Settings ST", "allowed_work_from_home_per_month")
	if allowed_work_from_home_per_month == None or allowed_work_from_home_per_month == "" or allowed_work_from_home_per_month == 0:
		frappe.throw(_("Please set the Allowed Work From Home Per Month in {0}").format(get_link_to_form("Stats Settings ST", "Stats Settings ST")))
	attendance_request_list = frappe.db.get_all("Attendance Request",
											filters={"employee":employee,"from_date":["between",[month_start, month_end]],"to_date":["between",[month_start, month_end]],"docstatus":1,"reason":"Work From Home"},
											fields=["sum(custom_work_from_home_days) as work_from_home_days"])
	if len(attendance_request_list)>0 and attendance_request_list[0].work_from_home_days:
		if (attendance_request_list[0].work_from_home_days + work_from_home_days) > allowed_work_from_home_per_month:
			frappe.throw(_("You cannot apply for more than {0} days of work from home in a month".format(allowed_work_from_home_per_month)))
		
def validate_total_amount_of_payment_table(self, method):
	if len(self.custom_payment_plan_details)>0:
		total_amount = 0
		for row in self.custom_payment_plan_details:
			if row.amount:
				total_amount = total_amount + row.amount
		if total_amount != self.custom_initial_cost:
			frappe.throw(_("Total Amount of Payment Schedule must be equal to Initial Cost"))
		
def set_log_type_based_on_device_id(self, method):
	if self.device_id:
		log_type = frappe.db.get_value("Device ID ST", self.device_id, "log_type")
		if log_type:
			self.log_type = log_type

def set_time_based_on_shift_time(self, method):
	consider_default_shift = True
	shift_details = get_employee_shift(self.employee, get_datetime(self.time), consider_default_shift, None)
	if self.get('time') and shift_details:
		if shift_details.actual_start:
			existing_same_timestamp_checkin = frappe.db.exists("Employee Checkin",{"employee":self.employee,"log_type":"IN","time":shift_details.actual_start})
			self.custom_physical_device_time = self.get('time')
			if existing_same_timestamp_checkin == None:
				self.shift = shift_details.shift_type.name
				self.offshift = 0
				if get_datetime(self.get('time')) < shift_details.actual_start and self.log_type=="IN":
					self.time = shift_details.actual_start
					self.custom_code_remarks = "For Attendance : IN : Early --> Shift Start"
			# else:
			# 	self.skip_auto_attendance = 1

@frappe.whitelist()
def inactive_employee_and_user_day_after_relieving_date():
	yesterday = add_days(getdate(nowdate()), -1)
	print(yesterday, '----yesterday--')
	employee_list = frappe.db.get_all('Employee', filters={'relieving_date': getdate(yesterday), 'status': 'Active'}, fields=['name'])

	if len(employee_list) > 0:
		for employee in employee_list:
			doc = frappe.get_doc('Employee', employee.name)
			doc.status = 'Left'
			doc.add_comment("Comment", text='Employee Status set to Left on {0} by system.'.format(getdate(nowdate())))
			doc.save(ignore_permissions=True)

			if doc.user_id:
				user = frappe.get_doc('User', doc.user_id)
				user.enabled = 0
				user.add_comment("Comment", text='User Status set to Disable on {0} by system.'.format(getdate(nowdate())))
				user.save(ignore_permissions=True)

def calculate_remaining_days_to_close_petty_cash_request():
	# Get all Petty Cash Requests that are not closed
	petty_cash_requests = frappe.get_all("Petty Cash Request ST", filters={"loan_status": "Open"}, fields=["name","creation_date"])
	petty_cash_grace_days = frappe.db.get_single_value("Stats Settings ST", "petty_cash_grace_days")
	if petty_cash_grace_days == None or petty_cash_grace_days == 0:
		frappe.throw(_("Please set the Petty Cash Grace Days in {0}").format(get_link_to_form("Stats Settings ST", "Stats Settings ST")))
	for request in petty_cash_requests:
		days_diff = date_diff(getdate(nowdate()), getdate(request.creation_date))
		remaining_days = petty_cash_grace_days - days_diff

		frappe.db.set_value("Petty Cash Request ST", request.name, "remaining_days_to_close_request", remaining_days)

def increase_one_hour_for_breast_feeding_request(self, method):
	if self.employee:
		grace_hour = frappe.db.get_single_value("Stats Settings ST", "employee_breast_feeding_grace_time") or 1
		consider_default_shift = True
		shift_details = get_employee_shift(self.employee, get_datetime(self.time), consider_default_shift, None)
		check_breast_feeding_request_exists = frappe.db.exists("Employee Breast Feeding Request ST", {"employee_no": self.employee, "docstatus": 1, "from_date": ["<=", getdate(self.time)], "to_date": [">=", getdate(self.time)]})
		if check_breast_feeding_request_exists:
			# If a request exists, increase the time by one hour
			early_late_time = frappe.db.get_value("Employee Breast Feeding Request ST", check_breast_feeding_request_exists, "early_late_time")
			if early_late_time:
				if early_late_time == _("Morning"):
					if self.log_type == "IN":
						# Check if an employee checkin exists for the same employee, log_type, and time
						check_employee_checkin_exists = frappe.db.get_all("Employee Checkin", 
														filters={"employee": self.employee, "log_type": "IN"},
														fields=["name","time"],
														order_by="time desc",
														limit=10)
						
						if len(check_employee_checkin_exists) > 0:
							for row in check_employee_checkin_exists:
								if getdate(self.time) == getdate(row.time):
									break
								else:
									self.custom_physical_device_time = self.time
									time_after_grace = add_to_date(get_datetime(self.time), hours=-(cint(grace_hour)))
									if shift_details and shift_details.actual_start:
										if time_after_grace < shift_details.actual_start:
											self.time = shift_details.actual_start
										else:
											self.time = time_after_grace
									self.custom_code_remarks = "Breast Feeding Request : IN --> -1 Hour"
									break
						else :
							time_after_grace = add_to_date(get_datetime(self.time), hours=-(cint(grace_hour)))
							if shift_details and shift_details.actual_start:
								if time_after_grace < shift_details.actual_start:
									self.time = shift_details.actual_start
								else:
									self.time = time_after_grace
							self.custom_code_remarks = "Breast Feeding Request : IN --> -1 Hour"
				if early_late_time == _("Afternoon"):
					if self.log_type == "OUT":
						self.custom_physical_device_time = self.time
						time_after_grace = add_to_date(get_datetime(self.time), hours=cint(grace_hour))

						if shift_details and shift_details.actual_end:
							if time_after_grace > shift_details.actual_end:
								checkin_exists_for_shift_end_time = frappe.db.exists("Employee Checkin",
															  {"employee":self.employee,"log_type":"OUT","time":shift_details.actual_end})

								if checkin_exists_for_shift_end_time:

									exists_checkin_physical_device_time = frappe.db.get_value("Employee Checkin",checkin_exists_for_shift_end_time,"custom_physical_device_time")
									frappe.db.set_value("Employee Checkin",checkin_exists_for_shift_end_time,"time",exists_checkin_physical_device_time)
									frappe.db.set_value("Employee Checkin",checkin_exists_for_shift_end_time,"custom_code_remarks","")

								self.time = shift_details.actual_end
							else:
								self.time = time_after_grace
						self.custom_code_remarks = "Breast Feeding Request : OUT --> +1 Hour"

@frappe.whitelist()
def set_no_of_leaves_in_draft_application(self,mehod):
	no_of_leaves_in_draft_application = 0
	if self.leave_type:
		all_leave_application = frappe.db.get_all("Leave Application",
											filters={"employee":self.employee,"docstatus":0,"leave_type":self.leave_type},
											fields=["name","total_leave_days"])
		if len(all_leave_application)>0:
			for leave_application in all_leave_application:
				if leave_application.total_leave_days:
					if leave_application.name != self.name:
						no_of_leaves_in_draft_application = no_of_leaves_in_draft_application + leave_application.total_leave_days
	self.custom_no_of_leaves_in_draft_application = no_of_leaves_in_draft_application

def transfer_employee_based_on_employee_transfer_st():
	employee_transfer_list = frappe.db.get_all("Employee Transfer ST",
											filters={"docstatus":1, "transfer_date":today()},
											fields=["name","employee_no","new_sub_department","new_main_department","new_direct_manager"])
	if len(employee_transfer_list)>0:
		for transfer in employee_transfer_list:
			employee_doc = frappe.get_doc("Employee",transfer.employee_no)
			# employee_is_manager = frappe.db.get_value("Employee",transfer.employee_no,"custom_is_manager")
			if employee_doc.custom_is_manager==1:
				main_department_manager = frappe.db.get_value("Department",transfer.new_main_department,"custom_main_department_manager")
				reports_to = main_department_manager
			else :
				reports_to = transfer.new_direct_manager
			
			employee_doc.department = transfer.new_main_department
			employee_doc.custom_sub_department = transfer.new_sub_department
			employee_doc.reports_to = reports_to
			employee_doc.add_comment("Comment",text=_("Employee's main department, sub department and report to is changed on {0} due to {1}".format(today(),get_link_to_form("Employee Transfer ST",transfer.name))))
			employee_doc.save(ignore_permissions=True)

def get_quater_start_end_date_from_current_date(current_date):
	month = getdate(current_date).month
	quater_start_date, quater_end_date = None, None
	print(month,type(month))
	current_year = getdate(today()).year
	if month in [1,2,3]:
		quater_start_date=getdate("{0}-01-01".format(current_year))
		quater_end_date=getdate("{0}-03-31".format(current_year))
		return quater_start_date, quater_end_date
	elif month in [4,5,6]:
		quater_start_date=getdate("{0}-04-01".format(current_year))
		quater_end_date=getdate("{0}-06-30".format(current_year))
		return quater_start_date, quater_end_date
	elif month in [7,8,9]:
		quater_start_date=getdate("{0}-07-01".format(current_year))
		quater_end_date=getdate("{0}-09-30".format(current_year))
		return quater_start_date, quater_end_date
	elif month in [10,11,12]:
		quater_start_date=getdate("{0}-10-01".format(current_year))
		quater_end_date=getdate("{0}-12-31".format(current_year))
		return quater_start_date, quater_end_date
	else :
		return quater_start_date, quater_end_date
	
@frappe.whitelist()
def validate_deputy_employee_if_applicable(self, method):
	apply_deputy_for_manager = frappe.db.get_single_value("Stats Settings ST", "apply_deputy_for_manager")
	apply_deputy_for_employee = frappe.db.get_single_value("Stats Settings ST", "apply_deputy_for_employee")
	no_of_days_required_for_deputy = frappe.db.get_single_value("Stats Settings ST", "deputy_required_for_no_of_days_of_leave")
	is_applicable_for_deputy = self.custom_is_manager
	if (is_applicable_for_deputy == 1 and is_applicable_for_deputy == apply_deputy_for_manager) or (is_applicable_for_deputy == 0 and is_applicable_for_deputy != apply_deputy_for_employee):
		if no_of_days_required_for_deputy:
			if cint(self.total_leave_days) >= no_of_days_required_for_deputy:
				if self.custom_deputy_employee == "" or self.custom_deputy_employee == None:
					frappe.throw(_("Deputy Employee is mandatory when total no of days is greater than or equal to {0}".format(no_of_days_required_for_deputy)))
				else:
					deputy_employee_status = frappe.db.get_value("Employee", self.custom_deputy_employee, "status")
					if deputy_employee_status != "Active":
						frappe.throw(_("Deputy Employee <b>{0}</b> is not active. Please select an active employee.".format(self.custom_deputy_employee_name)))
					if self.custom_deputy_employee == self.employee:
						frappe.throw(_("Deputy Employee cannot be the same as the employee applying for leave. Please select a different deputy employee."))
					else :
						validate_deputy_employee_not_apply_for_same_dates(self.from_date, self.to_date, self.custom_deputy_employee)
		else:
			frappe.throw(_("Please set Deputy Required for No of Days of Leave in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))

def create_journal_entry_for_petty_cash(doc,debit_account,credit_account,amount,department,je_date=None,party_type=None,party_name=None,jv_type=None):
	if je_date == None:
			je_date = today()

	payment_je_doc = frappe.new_doc("Journal Entry")
	payment_je_doc.voucher_type = "Journal Entry"
	payment_je_doc.posting_date = je_date

	if jv_type=="Procedure":
		payment_je_doc.custom_payment_procedure_reference = doc.name
	elif jv_type=="Closing":
		payment_je_doc.custom_petty_cash_closing_reference = doc.name
	elif jv_type=="Repayment":
		payment_je_doc.custom_petty_cash_re_payment_reference = doc.name

	accounts = []

	# company = erpnext.get_default_company()
	# company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")
	department_cost_center = frappe.db.get_value("Department",department,"custom_department_cost_center")

	accounts_row = {
		"account":debit_account,
		"cost_center":department_cost_center,
		"debit_in_account_currency":amount,
	}

	account_type = frappe.get_cached_value("Account",debit_account, "account_type")
	if account_type in ["Receivable", "Payable"]:
		accounts_row["party_type"]=party_type
		accounts_row["party"]=party_name

	accounts.append(accounts_row)
	accounts_row_2 = {
		"account":credit_account,
		"cost_center":department_cost_center,
		"credit_in_account_currency":amount,
	}
	account_type = frappe.get_cached_value("Account",credit_account, "account_type")
	if account_type in ["Receivable", "Payable"]:
		accounts_row_2["party_type"]=party_type
		accounts_row_2["party"]=party_name
	accounts.append(accounts_row_2)

	payment_je_doc.set("accounts",accounts)
	payment_je_doc.run_method('set_missing_values')
	payment_je_doc.save(ignore_permissions=True)
	payment_je_doc.submit()

	frappe.msgprint(_("Payment Journal Entry is created {0}").format(get_link_to_form("Journal Entry",payment_je_doc.name)),alert=1)

@frappe.whitelist()
def reset_education_allowance_balance_for_employee_dependants():

	education_year_list = frappe.db.get_all("Educational Year ST",fields=["educational_year_start_date"])
	employee_list = frappe.db.get_all("Employee",filters={"status":"Active"},fields=["name"])
	if len(education_year_list)>0:
		for row in education_year_list:
			if getdate(row.educational_year_start_date) == getdate(today()):
				if len(employee_list)>0:
					for employee in employee_list:
						employee_doc = frappe.get_doc("Employee",employee.name)
						education_allowance_amount = frappe.db.get_value("Employee Grade",employee_doc.grade,"custom_education_allowance_amount")
						if len(employee_doc.custom_dependants)>0:
							for child in employee_doc.custom_dependants:
								child.employee_education_allowance_balance = education_allowance_amount
						
						employee_doc.add_comment("Comment",text=_("Education Balance Amount of Dependants table is reset on {0} by the system".format(today())))
						employee_doc.save(ignore_permissions=True)

def set_gosi_deduction_type_in_employee(self, method):
	if self.custom_gosi_registration_date:
		stats_settings = frappe.get_doc('Stats Settings ST')
		self.custom_gosi_type = "Fixed"
		if len(stats_settings.gosi_deduction_increment_details) > 0:
			for gosi in stats_settings.gosi_deduction_increment_details:
				if getdate(self.custom_gosi_registration_date) >= getdate(gosi.from_date) and getdate(self.custom_gosi_registration_date) <= getdate(gosi.to_date):
					self.custom_gosi_type = "Vary"
					break

@frappe.whitelist()
def get_competencies_details_and_set_in_child_tables(sub_job_family):
	sub_job_family_doc = frappe.get_doc("Job Family ST",sub_job_family)

	basic_competencies_details = []
	leadership_competencies_details = []
	technical_competencies_details = []

	if len(sub_job_family_doc.competencies_library_details_table)>0:
		for row in sub_job_family_doc.competencies_library_details_table:
			if _(row.category) == _("Core"):
				basic_competencies_details.append({
					"competencies_name": row.competencies_name,
					"definition": row.definition,
					"elements": row.elements
				})
			elif _(row.category) == _("Leadership"):
				leadership_competencies_details.append({
					"competencies_name": row.competencies_name,
					"definition": row.definition,
					"elements": row.elements
				})
			elif _(row.category) == _("Technical"):
				technical_competencies_details.append({
					"competencies_name": row.competencies_name,
					"definition": row.definition,
					"elements": row.elements
				})

	return {"basic_competencies_details": basic_competencies_details,
			"leadership_competencies_details": leadership_competencies_details,
			"technical_competencies_details": technical_competencies_details
			}

@frappe.whitelist()
def fetch_definition_based_on_elements(level, elements):
	definition = "<table border=1>"
	definition += "<tr><th>Element</th><th>Definition</th></tr>"
	if elements:
		elements_list = elements.split(",")
		print(elements_list,"----elements_list---")
		if len(elements_list)>0:
			for element in elements_list:
				competencies_definition = frappe.db.get_value("Competencies Elements Details ST",{"parent":element,"level":level},"definition")
				# if competencies_definition:
				definition += "<tr><td>{0}</td><td>{1}</td></tr>".format(element, competencies_definition or "")
	definition += "</table>"
	return definition

def validate_past_dates_in_leave_application(self, method):
	if self.from_date and self.leave_type:
		max_allowed_days_to_apply_past_leave = frappe.db.get_value("Leave Type", self.leave_type, "custom_maximum_days_allowed_to_apply_past_date_leave")
		if max_allowed_days_to_apply_past_leave > 0:
			maximum_past_date_allowed = add_to_date(getdate(today()), days=-(max_allowed_days_to_apply_past_leave-1))
			if getdate(self.from_date) < getdate(maximum_past_date_allowed):
				frappe.throw(_("You are not allowed to apply leave for {0} from {1}.<br>You can apply leave from {2}".format(frappe.bold(self.leave_type), frappe.bold(self.from_date), frappe.bold(maximum_past_date_allowed))))

def get_doctype_workflow_state_list_for_progress_bar(doctype):
	workflow = frappe.db.get_value("Workflow", {"document_type": doctype, "is_active":1}, "name")

	state_list = []

	if workflow:
		workflow_doc = frappe.get_doc("Workflow", workflow)	
		for state in workflow_doc.transitions:
			if state.state not in state_list:
				state_list.append(state.state)
			if state.next_state not in state_list:
				state_list.append(state.next_state)

	return state_list

def progress_bar_html_onload(self, method):
	if self.get("workflow_state"):
		template_path = "templates/workflow_progressbar.html"
		workflow_states =get_doctype_workflow_state_list_for_progress_bar(self.doctype)
		html = frappe.render_template(template_path,  dict(workflow_states=workflow_states, doc=self.as_dict()))
		self.set_onload("workflow_progressbar_html", html)
		# print("=====Helllo======="*10)
	else:
		return
	
@frappe.whitelist()
def check_action_is_rejected(doctype, prev_workflow_state, workflow_state):
	# print(prev_workflow_state, "======prev_workflow_state=====")
	is_rejected = False
	workflow_name = frappe.db.get_value("Workflow",{"document_type":doctype,"is_active":1},"name")

	if workflow_name:
		workflow = frappe.get_doc("Workflow",workflow_name)
		current_state = workflow_state

		for state in workflow.transitions:
			if prev_workflow_state:
				if state.state == prev_workflow_state and state.next_state == current_state and state.custom_rejection_reason_require == 1:
					# print(state.idx, "------------>", state.custom_rejection_reason_require)
					is_rejected = True
					# print(is_rejected, "=============true is_rejected======")
					break
			elif state.next_state == current_state and state.custom_rejection_reason_require == 1:
				print(state.idx, "------------>", state.custom_rejection_reason_require)
				is_rejected = True
				# print(is_rejected, "=============true is_rejected======")
				break

	return is_rejected

@frappe.whitelist()
def add_reject_reason(doctype, docname, reject_reason):
	doc = frappe.get_doc(doctype, docname)
	doc.add_comment("Comment",text="Education Allowance Request is <b>Rejected</b>.<br>Reason: {0}".format(reject_reason))
	doc.save(ignore_permissions=True)

def reset_yearly_personal_permission_balance_in_employee():

	employee_list = frappe.db.sql("""
					SELECT
						e.name,
						e.custom_contract_type contract_type
					FROM
						`tabEmployee` e
					INNER JOIN `tabContract Type ST` ct
					ON
						e.custom_contract_type = ct.name
					WHERE
						ct.contract = 'Direct'
						and e.status = 'Active'
				""",as_dict=True)
	print(employee_list,"===list")
	if len(employee_list)>0:
		for employee in employee_list:
			employee_doc = frappe.get_doc("Employee",employee.name)
			yearly_permission_balance = frappe.db.get_value("Contract Type ST",employee.contract_type,"permission_balance_per_year")
			employee_doc.custom_permission_balance_per_year = yearly_permission_balance or 0
			employee_doc.add_comment("Comment",text=_("Permission Balance Per Year is reset to {0} on {1} by the system".format(yearly_permission_balance,today())))
			employee_doc.flags.ignore_mandatory = True
			employee_doc.flags.ignore_validate = True
			employee_doc.save(ignore_permissions=True)

def reset_monthly_personal_permission_balance_and_copy_existing_balance_to_previous_month_in_employee():

	employee_list = frappe.db.sql("""
					SELECT
						e.name,
						e.custom_contract_type
					FROM
						`tabEmployee` e
					INNER JOIN `tabContract Type ST` ct
					ON
						e.custom_contract_type = ct.name
					WHERE
						ct.contract = 'Civil'
						and e.status = 'Active'
				""",as_dict=True)
	print(employee_list,"===list")
	if len(employee_list)>0:
		for employee in employee_list:
			employee_doc = frappe.get_doc("Employee",employee.name)
			monthly_permission_balance = frappe.db.get_value("Contract Type ST",employee_doc.custom_contract_type,"permission_balance_per_month")
			employee_doc.custom_permission_balance_per_monthprevious = employee_doc.custom_permission_balance_per_monthcurrent
			employee_doc.custom_permission_balance_per_monthcurrent = monthly_permission_balance or 0
			employee_doc.add_comment("Comment",text=_("Permission Balance Per Month is reset to {0} on {1} by the system".format(monthly_permission_balance, today())))
			employee_doc.flags.ignore_mandatory = True
			employee_doc.flags.ignore_validate = True
			employee_doc.save(ignore_permissions=True)

def reset_monthly_compensatory_balance_to_zero_and_copy_existing_balance_to_previous_month_in_employee():

	employee_list = frappe.db.get_all("Employee",
								   filters={"status":"Active"},
								   fields=["name"])
	
	if len(employee_list)>0:
		for employee in employee_list:
			employee_doc = frappe.get_doc("Employee",employee.name)
			employee_doc.custom_compensatory_balance__previous_month_ = employee_doc.custom_compensatory_balance__current_month__
			employee_doc.custom_compensatory_balance__current_month__ = 0
			employee_doc.add_comment("Comment",text=_("Compensatory Balance Per Month is reset to {0} on {1} by the system".format(0, today())))
			employee_doc.flags.ignore_mandatory = True
			employee_doc.flags.ignore_validate = True
			employee_doc.save(ignore_permissions=True)

def previous_month_permission_balance_and_compensatory_balance_set_to_zero():
	employee_list = frappe.db.get_all("Employee",
								   filters={"status":"Active"},
								   fields=["name"])
	if len(employee_list)>0:
		for employee in employee_list:
			employee_doc = frappe.get_doc("Employee",employee.name)
			employee_doc.custom_permission_balance_per_monthprevious = 0
			employee_doc.custom_compensatory_balance__previous_month_ = 0
			employee_doc.add_comment("Comment",text=_("Previous month Compensatory Balance and Permission Balance is reset to {0} on {1} by the system".format(0, today())))
			employee_doc.flags.ignore_mandatory = True
			employee_doc.flags.ignore_validate = True
			employee_doc.save(ignore_permissions=True)

def calculate_extra_working_hours(self,method):
	print('-4'*10)
	print('calculate_extra_working_hours'*10)
	shift_start_time = frappe.db.get_value("Shift Type",self.shift,"start_time")
	shift_end_time = frappe.db.get_value("Shift Type",self.shift,"end_time")

	actual_working_minutes = self.custom_working_minutes_per_day
	employee_working_hours = self.working_hours

	# rounded_employee_working_hours = rounded(employee_working_hours - actual_working_hours, 0)
	if employee_working_hours and (employee_working_hours > 0):
		employee_working_minutes = employee_working_hours * 60
		self.custom_actual_working_minutes = employee_working_minutes
		if self.custom_net_working_minutes==None or self.custom_net_working_minutes == 0:
			print("0 net hours ------------------------------")
			self.custom_net_working_minutes = self.custom_actual_working_minutes

		# if employee_working_minutes > actual_working_minutes:
		total_extra_min = employee_working_minutes - actual_working_minutes
		self.custom_extra_minutes = total_extra_min
	
	if not self.custom_attendance_type:
		if self.status:
			self.custom_attendance_type = self.status

def calculate_working_minutes_based_on_permission_request_or_work_out_of_office(self, method):
	shift_start_time = frappe.db.get_value("Shift Type",self.shift,"start_time")
	shift_end_time = frappe.db.get_value("Shift Type",self.shift,"end_time")

	allowed_attendance_grace_time = frappe.db.get_single_value("Stats Settings ST","allowed_attendance_grace_time")

	if allowed_attendance_grace_time == None or allowed_attendance_grace_time == 0:
		frappe.throw(_("Please set Allowed Attendance Grace Time in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
	print(self.working_hours,"----working_hours---")
	actual_working_minutes = (self.working_hours or 0) * 60
	self.custom_actual_working_minutes = actual_working_minutes

	permission_request_exists = frappe.db.get_all("Employee Permission Request ST",
											   filters={"docstatus":1,"employee_no":self.employee,"type_of_request":"Permission Request","request_date":self.attendance_date},
											   fields=["name","total_minutes"])
	permitted_minutes_for_permission_request = 0
	permitted_minutes_for_work_out_of_office = 0
	working_minutes_after_permission = actual_working_minutes
	working_minutes_after_work_out_office = actual_working_minutes
	time_outside_office = self.custom_working_minutes_per_day - self.custom_actual_working_minutes
	print(time_outside_office,"----time_outside_office------------------------")
	self.custom_time_spent_outside_office = time_outside_office

	if self.status != "Absent":
		if actual_working_minutes < self.custom_working_minutes_per_day:
			if len(permission_request_exists)>0:
				for row in permission_request_exists:
					if row.total_minutes:
						working_minutes_after_permission = working_minutes_after_permission + row.total_minutes
						if working_minutes_after_permission > self.custom_working_minutes_per_day:
							extra_minutes = working_minutes_after_permission - self.custom_working_minutes_per_day
							permitted_minutes_for_permission_request = row.total_minutes - extra_minutes
							actual_working_minutes = actual_working_minutes + permitted_minutes_for_permission_request

						else:
							permitted_minutes_for_permission_request = row.total_minutes
							actual_working_minutes = working_minutes_after_permission
					self.custom_employee_permission_doctype = "Employee Permission Request ST"
					self.custom_employee_permission_reference = row.name
	
	if self.status != "Absent":
		work_out_of_office_exists = frappe.db.get_all("Employee Work Out of Office ST",
												filters={"docstatus":1,"employee_no":self.employee,"from_date":["<=",self.attendance_date],"to_date":[">=",self.attendance_date]},
												fields=["name","total_minutes_per_day"])
		if actual_working_minutes < self.custom_working_minutes_per_day:
			if len(work_out_of_office_exists)>0:
				for row in work_out_of_office_exists:
					if row.total_minutes_per_day:
						working_minutes_after_work_out_office = working_minutes_after_work_out_office + row.total_minutes_per_day
						if working_minutes_after_work_out_office > self.custom_working_minutes_per_day:
							extra_minutes = working_minutes_after_work_out_office - self.custom_working_minutes_per_day
							permitted_minutes_for_work_out_of_office = row.total_minutes_per_day - extra_minutes
							actual_working_minutes = actual_working_minutes + permitted_minutes_for_work_out_of_office

						else:
							permitted_minutes_for_work_out_of_office = row.total_minutes_per_day
							actual_working_minutes = working_minutes_after_work_out_office
					self.custom_employee_permission_doctype = "Employee Work Out of Office ST"
					self.custom_employee_permission_reference = row.name

	self.custom_erpnext_calculated_working_hours = self.working_hours
	self.custom_net_working_minutes = actual_working_minutes

	if self.status != "Absent":
		working_minutes_with_grace = actual_working_minutes + (allowed_attendance_grace_time or 0)
	else:
		working_minutes_with_grace = actual_working_minutes

	final_working_minutes_with_grace = 0

	if working_minutes_with_grace >= self.custom_working_minutes_per_day :
		final_working_minutes_with_grace = self.custom_working_minutes_per_day
	else:
		final_working_minutes_with_grace = working_minutes_with_grace
	
	self.custom_working_minutes_with_grace = final_working_minutes_with_grace
	# self.custom_actual_working_minutes = actual_working_minutes
	self.custom_balance_used_mins = permitted_minutes_for_permission_request

	shortage_to_complete_working_minutes = self.custom_working_minutes_per_day - final_working_minutes_with_grace
	if shortage_to_complete_working_minutes < 0:
		shortage_to_complete_working_minutes = 0
	
	if actual_working_minutes > self.custom_working_minutes_per_day:
		extra_working_minutes = actual_working_minutes - self.custom_working_minutes_per_day
	else:
		extra_working_minutes = 0
	self.custom_shortage_to_complete_working_hours = shortage_to_complete_working_minutes
	self.custom_extra_minutes = extra_working_minutes

	final_working_hours = rounded(final_working_minutes_with_grace / 60, 2)
	self.working_hours = final_working_hours

def deduct_permission_balance_and_compensatory_balance_from_employee(self, method):
	if self.custom_employee_permission_doctype and self.custom_employee_permission_reference:
		if self.custom_employee_permission_doctype == "Employee Permission Request ST":
			permission_request_doc = frappe.get_doc("Employee Permission Request ST",self.custom_employee_permission_reference)

			### deduct permission balance or compensatory balance from employee based on consumption type in permission request

			if permission_request_doc.total_minutes and permission_request_doc.type_of_request == "Permission Request":
				contract = permission_request_doc.contract
				if permission_request_doc.consumption_type == "Deduct From Permission Balance":

					if contract == "Civil":
						employee_doc = frappe.get_doc("Employee",self.employee)
						if employee_doc.custom_permission_balance_per_monthcurrent and (employee_doc.custom_permission_balance_per_monthcurrent > 0):
							if employee_doc.custom_permission_balance_per_monthcurrent >= self.custom_balance_used_mins:
								remaining_balance = employee_doc.custom_permission_balance_per_monthcurrent - self.custom_balance_used_mins

								employee_doc.add_comment("Comment",text=_("Permission Balance is deducted by {0} minutes on {1} due to Employee Permission Request {2}.".format(self.custom_balance_used_mins,today(),get_link_to_form("Employee Permission Request ST",permission_request_doc.name))))
								employee_doc.flags.ignore_mandatory = True
								employee_doc.flags.ignore_validate = True
								employee_doc.save(ignore_permissions=True)
								frappe.db.set_value("Employee",self.employee,"custom_permission_balance_per_monthcurrent",remaining_balance)

							permission_request_doc.add_comment("Comment",text=_("Permission Balance of {0} minutes is deducted from employee on {1}.".format(self.custom_balance_used_mins,today())))
							permission_request_doc.flags.ignore_mandatory = True
							permission_request_doc.save(ignore_permissions=True)
						else:
							frappe.throw(_("Employee {0} does not have sufficient Permission Balance to cover the requested minutes of {1}.".format(self.employee_name, permission_request_doc.total_minutes)))

					elif contract == "Direct":
						employee_doc = frappe.get_doc("Employee",self.employee)
						if employee_doc.custom_permission_balance_per_year and (employee_doc.custom_permission_balance_per_year > 0):
							if employee_doc.custom_permission_balance_per_year >= self.custom_balance_used_mins:
								remaining_balance = employee_doc.custom_permission_balance_per_year - self.custom_balance_used_mins
								employee_doc.custom_permission_balance_per_year = remaining_balance
								employee_doc.add_comment("Comment",text=_("Permission Balance is deducted by {0} minutes on {1} due to Employee Permission Request {2}.".format(self.custom_balance_used_mins,today(),get_link_to_form("Employee Permission Request ST",permission_request_doc.name))))
								employee_doc.flags.ignore_mandatory = True

								employee_doc.save(ignore_permissions=True)

								frappe.db.set_value("Employee",self.employee,"custom_permission_balance_per_year",remaining_balance)
							permission_request_doc.add_comment("Comment",text=_("Permission Balance of {0} minutes is deducted from employee on {1}.".format(self.custom_balance_used_mins,today())))
							permission_request_doc.flags.ignore_mandatory = True
							permission_request_doc.save(ignore_permissions=True)
						else:
							frappe.throw(_("Employee {0} does not have sufficient Permission Balance to cover the requested minutes of {1}.".format(self.employee_name, permission_request_doc.total_minutes)))

				elif permission_request_doc.consumption_type == "Deduct From Compensatory Balance":
						employee_doc = frappe.get_doc("Employee",self.employee)
						if employee_doc.custom_compensatory_balance__current_month__ and (employee_doc.custom_compensatory_balance__current_month__ > 0):
							if employee_doc.custom_compensatory_balance__current_month__ >= self.custom_balance_used_mins:
								remaining_balance = employee_doc.custom_compensatory_balance__current_month__ - self.custom_balance_used_mins
								employee_doc.add_comment("Comment",text=_("Compensatory Balance is deducted by {0} minutes on {1} due to Employee Permission Request {2}.".format(self.custom_balance_used_mins,today(),get_link_to_form("Employee Permission Request ST",permission_request_doc.name))))
								employee_doc.flags.ignore_mandatory = True
								employee_doc.save(ignore_permissions=True)
								frappe.db.set_value("Employee",self.employee,"custom_compensatory_balance__current_month__",remaining_balance)
							permission_request_doc.add_comment("Comment",text=_("Compensatory Balance of {0} minutes is deducted from employee on {1}.".format(self.custom_balance_used_mins,today())))
							permission_request_doc.flags.ignore_mandatory = True
							permission_request_doc.save(ignore_permissions=True)
						else:
							frappe.throw(_("Employee {0} does not have sufficient Compensatory Balance to cover the requested minutes of {1}.".format(self.employee_name, permission_request_doc.total_minutes)))

	### if there is extra working minutes, add to compensatory balance of employee
	if self.custom_extra_minutes and (self.custom_extra_minutes > 0):
		employee_doc = frappe.get_doc("Employee",self.employee)
		if employee_doc.custom_compensatory_balance__current_month__ == None:
			employee_doc.custom_compensatory_balance__current_month__ = 0
		employee_doc.custom_compensatory_balance__current_month__ = employee_doc.custom_compensatory_balance__current_month__ + self.custom_extra_minutes

		employee_doc.add_comment("Comment",text=_("Compensatory Balance is increased by {0} minutes on {1} due to extra working minutes in attendance {2}.".format(self.custom_extra_minutes,today(),get_link_to_form("Attendance",self.name))))
		employee_doc.flags.ignore_mandatory = True
		employee_doc.save(ignore_permissions=True)