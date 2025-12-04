import frappe
from frappe import _
from frappe.utils import (add_to_date, get_datetime, getdate, nowdate, get_first_day, cint, get_link_to_form, flt, cstr, today)
from stats.stats.report.employee_attendance.employee_attendance import calculate_incomplete_total_monthly_minutes

########### LWP Deduction ###########

def get_non_working_days(employee, payroll_start_date, payroll_end_date) -> float:
	filters = {
		"docstatus": 1,
		"status": "On Leave",
		"employee": employee,
		"attendance_date": ("between", [get_datetime(payroll_start_date), get_datetime(payroll_end_date)]),
	}

	# if status == "On Leave":
	lwp_leave_types = frappe.get_all("Leave Type", filters={"is_lwp": 1}, pluck="name")
	filters["leave_type"] = ("IN", lwp_leave_types)

	record = frappe.get_all("Attendance", filters=filters, fields=["COUNT(*) as total_lwp"])
	return record[0].total_lwp if len(record) else 0

@frappe.whitelist()
def calculate_lwp_dedution(payroll_entry):
	payroll_entry = frappe.get_doc("Payroll Entry", payroll_entry)
	previous_month_start_date = add_to_date(payroll_entry.start_date,months=-1)
	previous_month_last_date = add_to_date(payroll_entry.start_date,days=-1)

	print(previous_month_last_date, previous_month_start_date,'----------previous_month_last_date-----------')

	emp_dedution_list = []
	for emp in payroll_entry.employees:
		total_lwp = get_non_working_days(emp.employee,previous_month_start_date, previous_month_last_date)
		print(total_lwp, '--total_lwp')

		emp_dedution_details = {}

		if total_lwp > 0:
			salary_assignment = frappe.db.get_all("Salary Structure Assignment",
								  fields=["name", "salary_structure"], filters={"from_date": ["<=", payroll_entry.start_date], "employee":emp.employee, "docstatus":1},
								  order_by = "from_date desc", limit=1)
			# print(salary_assignment[0].name, '--salary_assignment')
			if len(salary_assignment) > 0:
				ss = frappe.get_doc("Salary Structure", salary_assignment[0].salary_structure)

				total_lwp_deduction = 0
				for ear in ss.earnings:
					deduction_component = frappe.db.get_value("Salary Component", ear.salary_component, 'custom_consider_for_deduction_calculation')
					if deduction_component == 1:
						per_day_salary = (ear.amount)/30
						total_lwp_deduction = total_lwp_deduction + (per_day_salary * total_lwp)

				emp_dedution_details['employee'] = emp.employee
				emp_dedution_details['lwp_deduction'] = total_lwp_deduction
				print(total_lwp_deduction, '---total_lwp_deduction')

				emp_dedution_list.append(emp_dedution_details)

		else:
			emp_dedution_details['employee'] = emp.employee
			emp_dedution_details['lwp_deduction'] = 0

			emp_dedution_list.append(emp_dedution_details)

	return emp_dedution_list

########### Absent Deduction ###########

def get_absent_days(employee, payroll_start_date, payroll_end_date) -> float:
	filters = {
		"docstatus": 1,
		"status": "Absent",
		"employee": employee,
		"attendance_date": ("between", [get_datetime(payroll_start_date), get_datetime(payroll_end_date)]),
	}

	record = frappe.get_all("Attendance", filters=filters, fields=["COUNT(*) as total_absent"])
	return record[0].total_absent if len(record) else 0


@frappe.whitelist()
def calculate_absent_dedution(payroll_entry):
	payroll_entry = frappe.get_doc("Payroll Entry", payroll_entry)
	previous_month_start_date = add_to_date(payroll_entry.start_date,months=-1)
	previous_month_last_date = add_to_date(payroll_entry.start_date,days=-1)

	print(previous_month_last_date, previous_month_start_date,'----------previous_month_last_date-----------')

	emp_dedution_list = []
	for emp in payroll_entry.employees:
		total_absent = get_absent_days(emp.employee, previous_month_start_date, previous_month_last_date)
		print(total_absent, '--total_absent')

		emp_dedution_details = {}

		if total_absent > 0:
			salary_assignment = frappe.db.get_all("Salary Structure Assignment",
								  fields=["name", "salary_structure"], filters={"from_date": ["<=", payroll_entry.start_date], "employee":emp.employee, "docstatus":1},
								  order_by = "from_date desc", limit=1)
			# print(salary_assignment[0].name, '--salary_assignment')
			if len(salary_assignment) > 0:
				ss = frappe.get_doc("Salary Structure", salary_assignment[0].salary_structure)

				total_absent_deduction = 0
				for ear in ss.earnings:
					deduction_component = frappe.db.get_value("Salary Component", ear.salary_component, 'custom_consider_for_deduction_calculation')
					if deduction_component == 1:
						per_day_salary = (ear.amount)/30
						total_absent_deduction = total_absent_deduction + (per_day_salary * total_absent)

				emp_dedution_details['employee'] = emp.employee
				emp_dedution_details['absent_deduction'] = total_absent_deduction
				print(total_absent_deduction, '---total_absent_deduction')

				emp_dedution_list.append(emp_dedution_details)

		else:
			emp_dedution_details['employee'] = emp.employee
			emp_dedution_details['absent_deduction'] = 0

			emp_dedution_list.append(emp_dedution_details)

	return emp_dedution_list

########### Incomplete Monthly Mins Deduction ###########

@frappe.whitelist()
def calculate_incomplete_monthly_mins_deduction(payroll_entry):
	payroll_entry = frappe.get_doc("Payroll Entry", payroll_entry)
	previous_month_start_date = add_to_date(payroll_entry.start_date,months=-1)
	previous_month_last_date = add_to_date(payroll_entry.start_date,days=-1)
	print(payroll_entry.name, "000=======payroll_entry======")

	consider_incomplete_monthly_mins = frappe.db.get_single_value('Stats Settings ST', 'consider_incomplete_monthly_mins')

	emp_monthly_incomplete_mins_list = []

	if consider_incomplete_monthly_mins == 1:

		for emp in payroll_entry.employees:

			total_incomplete_monthly_mins = calculate_incomplete_total_monthly_minutes(emp.employee, previous_month_start_date, previous_month_last_date)
			contract_type = frappe.db.get_value("Employee", emp.employee, "custom_contract_type")
			total_mins_per_month = frappe.db.get_value("Contract Type ST", contract_type, "total_mins_per_month")
			total_hours_per_day = frappe.db.get_value("Contract Type ST", contract_type, "total_hours_per_day")

			emp_incomplete_mins_details = {}

			print(total_incomplete_monthly_mins, "---total_incomplete_monthly_mins")
			print(total_mins_per_month, "======total_mins_per_month")
			if total_incomplete_monthly_mins < total_mins_per_month:

				salary_assignment = frappe.db.get_all("Salary Structure Assignment",
									fields=["name", "salary_structure"], filters={"from_date": ["<=", payroll_entry.start_date], "employee":emp.employee, "docstatus":1},
									order_by = "from_date desc", limit=1)

				if len(salary_assignment) > 0:
					ss = frappe.get_doc("Salary Structure", salary_assignment[0].salary_structure)
					total_incomplete_mins_deduction = 0
					for ear in ss.earnings:
						deduction_component = frappe.db.get_value("Salary Component", ear.salary_component, 'custom_consider_for_deduction_calculation')
						if deduction_component == 1:
							per_mins_salary = (ear.amount)/(30 * total_hours_per_day * 60)
							total_incomplete_mins_deduction = total_incomplete_mins_deduction + (per_mins_salary * total_incomplete_monthly_mins)

							emp_incomplete_mins_details['employee'] = emp.employee
							emp_incomplete_mins_details['incomplete_mins_deduction'] = total_incomplete_mins_deduction
							print(total_incomplete_mins_deduction, '---total_incomplete_mins_deduction')

							emp_monthly_incomplete_mins_list.append(emp_incomplete_mins_details)

			else:
				emp_incomplete_mins_details['employee'] = emp.employee
				emp_incomplete_mins_details['incomplete_mins_deduction'] = 0

				emp_monthly_incomplete_mins_list.append(emp_incomplete_mins_details)

	return emp_monthly_incomplete_mins_list


########### Deduction Additional Salary ###########

def create_additonal_salary_for_deduction(self, method):

	lwp_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'lwpabsent_deduction_component')
	absent_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'absent_deduction_component')
	incomplete_monthly_mins_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'incomplete_monthly_mins_deduction_component')

	for emp in self.employees:
		if emp.custom_lwp_deduction > 0:
			additional_salary = frappe.new_doc("Additional Salary")
			additional_salary.employee = emp.employee
			additional_salary.payroll_date = self.start_date
			additional_salary.salary_component =  lwp_deduction_component
			additional_salary.overwrite_salary_structure_amount = 0
			additional_salary.amount = emp.custom_lwp_deduction
			additional_salary.save(ignore_permissions=True)
			additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for LWP Deduction'.format(nowdate()))
			frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, emp.employee), alert=1)
			additional_salary.submit()

		if emp.custom_absent_deduction > 0:
			additional_salary = frappe.new_doc("Additional Salary")
			additional_salary.employee = emp.employee
			additional_salary.payroll_date = self.start_date
			additional_salary.salary_component =  absent_deduction_component
			additional_salary.overwrite_salary_structure_amount = 0
			additional_salary.amount = emp.custom_absent_deduction
			additional_salary.save(ignore_permissions=True)
			additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for Absent Deduction'.format(nowdate()))
			frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, emp.employee), alert=1)
			additional_salary.submit()

		if emp.custom_incomplete_monthly_mins_deduction > 0:
			additional_salary = frappe.new_doc("Additional Salary")
			additional_salary.employee = emp.employee
			additional_salary.payroll_date = self.start_date
			additional_salary.salary_component =  incomplete_monthly_mins_deduction_component
			additional_salary.overwrite_salary_structure_amount = 0
			additional_salary.amount = emp.custom_incomplete_monthly_mins_deduction
			additional_salary.save(ignore_permissions=True)
			additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for Incomplete Monthly Mins Deduction'.format(nowdate()))
			frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, emp.employee), alert=1)
			additional_salary.submit()


########### Employee Resignation Additional Salary ###########

def create_resignation_addition_salary_for_employee(self, method):
	print('---create_resignation_addition_salary_for_employee---')
	relieving_date_changed = self.has_value_changed("relieving_date")

	print(relieving_date_changed, '----------relieving_date_changed')
	if relieving_date_changed and self.relieving_date != None:

		salary_assignment = frappe.db.get_all("Salary Structure Assignment",
								  fields=["name", "salary_structure"], filters={"from_date": ["<=", nowdate()], "employee":self.name, "docstatus":1},
								  order_by = "from_date desc", limit=1)

		if len(salary_assignment) > 0:
			print(salary_assignment[0].name, '--salary_assignment')

			ss = frappe.get_doc("Salary Structure", salary_assignment[0].salary_structure)

			total_deduction = 0
			for ear in ss.earnings:
				deduction_component = frappe.db.get_value("Salary Component", ear.salary_component, 'custom_consider_for_deduction_calculation')
				if deduction_component == 1:
					per_day_salary = (ear.amount)/30
					days_after_resignation = 30 - getdate(self.relieving_date).day
					total_deduction = (total_deduction) + (per_day_salary * days_after_resignation)


			if total_deduction > 0:
				resignation_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'resignation_deduction_component')
				print(resignation_deduction_component, '--resignation_deduction_component')
				if not resignation_deduction_component:
					frappe.throw(_("Please Set Resignation Deduction in Stats Settings Doctype"))
				else:
					additional_salary = frappe.new_doc("Additional Salary")
					additional_salary.employee = self.name
					# additional_salary.payroll_date =  get_first_day(next_month_date)
					additional_salary.payroll_date = get_first_day(self.relieving_date)
					print(self.relieving_date, additional_salary.payroll_date, '--------')
					additional_salary.salary_component =  resignation_deduction_component
					additional_salary.overwrite_salary_structure_amount = 0
					additional_salary.amount = total_deduction
					additional_salary.save(ignore_permissions=True)
					additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for Resignation Deduction'.format(nowdate()))
					frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, self.name), alert=1)
					additional_salary.submit()

			else:
				frappe.msgprint(_("Additional Salary is not Created for Employee {0}, becasue No Salary Earning Component Considers for Deduction.").format(self.name), alert=1)

		else:
			frappe.throw(_("No Salary Structure Assignment Found For {0} Employee").format(self.name))


########### Employee Joining Additional Salary ###########
def create_addtional_salary_for_new_joinee(self, method):
	payroll_date = frappe.db.get_single_value('Stats Settings ST', 'every_month_payroll_date')
	earning_component = frappe.db.get_single_value('Stats Settings ST', 'default_new_hire_earning_component')
	due_component = frappe.db.get_single_value('Stats Settings ST', 'default_new_hire_due_component')

	if payroll_date == None:
			frappe.throw(_("Please Set Every Month Payroll Date In Stats Settings."))

	if len(self.employees) > 0:
		last_month_payroll_date = add_to_date(self.start_date, months=-1)

		for emp in self.employees:
			joining_date = frappe.get_value("Employee", emp.employee, 'date_of_joining')
			salary_assignment = get_latest_salary_structure_assignment(emp.employee, getdate(joining_date))
			print(salary_assignment, "======salary_assignment====")
			total_monthly_salary = frappe.db.get_value("Salary Structure Assignment", salary_assignment, "base")
			per_day_salary = total_monthly_salary/30

			#### joining date is before payroll date: deducte salary of non working days #### 
			if getdate(joining_date).day < cint(getdate(payroll_date).day):
				if getdate(self.start_date).year == getdate(joining_date).year and getdate(self.start_date).month == getdate(joining_date).month:
					no_of_non_working_days = getdate(joining_date).day - 1

					if no_of_non_working_days > 0:
						total_deduction = per_day_salary * no_of_non_working_days

						additional_salary = frappe.new_doc("Additional Salary")
						additional_salary.employee = emp.employee
						additional_salary.payroll_date = getdate(joining_date)
						additional_salary.salary_component =  due_component
						additional_salary.overwrite_salary_structure_amount = 0
						additional_salary.amount = total_deduction
						additional_salary.save(ignore_permissions=True)
						additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for New Joining Salary'.format(nowdate()))
						frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, self.name), alert=1)
						additional_salary.submit()
				else:
					pass

			#### joining date is after payroll date: add salary to next month ####
			elif getdate(joining_date).day >= cint(getdate(payroll_date).day):
				if getdate(last_month_payroll_date).year == getdate(joining_date).year and getdate(last_month_payroll_date).month == getdate(joining_date).month:
					no_of_working_days = (30 - getdate(joining_date).day) + 1
					total_earnings = per_day_salary * no_of_working_days

					additional_salary = frappe.new_doc("Additional Salary")
					additional_salary.employee = emp.employee
					additional_salary.payroll_date = self.start_date
					additional_salary.salary_component =  earning_component
					additional_salary.overwrite_salary_structure_amount = 0
					additional_salary.amount = total_earnings
					additional_salary.save(ignore_permissions=True)
					additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for New Joining Salary'.format(nowdate()))
					frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, self.name), alert=1)
					additional_salary.submit()
				else:
					pass

def get_latest_salary_structure_assignment(employee, from_date):
	salary_assignment = frappe.db.get_all("Salary Structure Assignment",
								  fields=["name", "salary_structure", "base"], filters={"from_date": ["<=", from_date], "employee":employee, "docstatus":1},
								  order_by = "from_date desc", limit=1)
	if len(salary_assignment) > 0:
		return salary_assignment[0].name
	else:
		frappe.throw(_("For {0} date No Salary Structure Assignment Found for {1} Employee").format(from_date, employee))

def validate_salary_amount_in_grade(self, method):
	### basic salary amount
	if (self.custom_minimum_basic_amount > self.custom_mid_basic_amount) or (self.custom_minimum_basic_amount > self.custom_max_basic_amount):
		frappe.throw(_("Minimum Basic Amount should be less than mid & max basic amount."))

	elif (self.custom_max_basic_amount < self.custom_minimum_basic_amount) or (self.custom_max_basic_amount < self.custom_mid_basic_amount):
		frappe.throw(_("Maximum Basic Amount should be more than mid & max basic amount."))

	elif (self.custom_mid_basic_amount > self.custom_max_basic_amount) or (self.custom_minimum_basic_amount > self.custom_mid_basic_amount):
		frappe.throw(_("Mid Basic Amount should be more than minimum & less than max basic amount."))

	### earning tables
	basic_salary_component = self.custom_basic_salary_component
	if len(self.custom_earnings) > 0:
		for ear in self.custom_earnings:
			if ear.earning == basic_salary_component:
				frappe.throw(_("In Earnings Details Row {0}: You cannot select Basic Salary Component Multiple Time").format(ear.idx))
			elif ear.maximum_amount < ear.minimum_amount:
				frappe.throw(_("In Earnings Details Row {0}: Maximum Amount Cannot Be Less than Minimum Amount").format(ear.idx))
			else:
				continue

	if len(self.custom_other_earnings) > 0:
		for ear in self.custom_other_earnings:
			if ear.earning == basic_salary_component:
				frappe.throw(_("In Other Earnings Details Row {0}: You cannot select Basic Salary Component Multiple Time").format(ear.idx))
			if ear.method == 'Percentage':
				if ear.maximum_amount and ear.minimum_amount and ear.maximum_amount < ear.minimum_amount:
					frappe.throw(_("In Other Earnings Details Row {0}:Maximum Amount cannot Be Less than Minimum Amount").format(ear.idx))

def get_latest_basic_salary_of_employee(employee,date=None):
	basic_salary = 0
	employee_grade = frappe.db.get_value("Employee",employee,"grade")
	if employee_grade:
		basic_salary_component = frappe.db.get_value("Employee Grade",employee_grade,"custom_basic_salary_component")
	else:
		frappe.throw(_("Please set employee grade in Employee {0}".format(get_link_to_form("Employee",employee))))
	if date == None:
		date = nowdate()
	latest_salary_structure_assignment = get_latest_salary_structure_assignment(employee,date)
	if latest_salary_structure_assignment:
		latest_salary_structure = frappe.db.get_value("Salary Structure Assignment",latest_salary_structure_assignment,"salary_structure")
		if latest_salary_structure:
			salary_structure_doc = frappe.get_doc("Salary Structure",latest_salary_structure)
			if len(salary_structure_doc.earnings)>0:
				for earning_row in salary_structure_doc.earnings:
					if basic_salary_component:
						if earning_row.salary_component == basic_salary_component:
							basic_salary = earning_row.amount
							break
	else:
		frappe.throw(_("No latest Salary Structure Assignment found for employee {0}".format(get_link_to_form("Employee",employee))))
	return basic_salary

def get_gosi_deduction_compenent_formula_and_name(employee):
	gosi_details = {}
	emp_grade = frappe.db.get_value("Employee", employee, "grade")
	if emp_grade:
		grade_doc = frappe.get_doc("Employee Grade", emp_grade)
		if len(grade_doc.custom_deduction) > 0:
			for ded in grade_doc.custom_deduction:
				is_gosi = frappe.db.get_value("Salary Component", ded.deduction, 'custom_is_gosi_deduction')
				if is_gosi == 1:
					gosi_details['gosi_component'] = ded.deduction
					gosi_details['gosi_formula'] = ded.formula
					break

	return gosi_details

def get_gosi_deduction_amount(salary_structure, formula, gosi_component, gosi_percentage):
	# print(formula, "=====================formula=================")
	ss = frappe.get_doc("Salary Structure", salary_structure)
	salary_abbreviation_dict = {}
	# MAX_BAS_HAL
	max_bas_hal = frappe.db.get_single_value('Stats Settings ST', 'max_bas_hal')
	salary_abbreviation_dict["MAX_BAS_HAL"] = max_bas_hal or 0
	salary_abbreviation_dict["GOSI_PERCENTAGE"] = flt(gosi_percentage) / 100
	new_gosi_deduction_amount = 0
	old_gosi_deduction_amount = 0

	if len(ss.earnings) > 0:
		for ear in ss.earnings:
			salary_abbreviation_dict[ear.abbr] = ear.amount

	if len(ss.deductions) > 0:
		for ded in ss.deductions:
			is_gosi = frappe.db.get_value("Salary Component", ded.salary_component, 'custom_is_gosi_deduction')
			if _(ded.salary_component) == _(gosi_component):
				new_gosi_deduction_amount = flt(frappe.safe_eval(formula, None,salary_abbreviation_dict), 2)
				old_gosi_deduction_amount = ded.amount
	# print(new_gosi_deduction_amount, "====new_gosi_deduction_amount====", old_gosi_deduction_amount, "==========old_gosi_deduction_amount===", salary_abbreviation_dict["GOSI_PERCENTAGE"], "===================")
	return new_gosi_deduction_amount, old_gosi_deduction_amount

def create_salary_structure_for_gosi(old_salary_structure, employee, gosi_component, gosi_amount, gosi_percentage, gosi_date):
	old_ss = frappe.get_doc("Salary Structure", old_salary_structure)

	new_ss = frappe.new_doc("Salary Structure")
	new_ss.__newname = employee + "/GOSI-" + cstr(gosi_percentage)
	new_ss.name = employee + "/GOSI-" + cstr(gosi_percentage)
	new_ss.custom_employee_no = employee
	new_ss.custom_type_of_creation = "GOSI"

	if len(old_ss.earnings) > 0:
		for ear in old_ss.earnings:
			earning = new_ss.append("earnings", {})
			earning.salary_component = ear.salary_component
			earning.amount = ear.amount
			earning.amount_based_on_formula = 0
			earning.is_tax_applicable = 0
			earning.depends_on_payment_days = 0

	if len(old_ss.deductions) > 0:
		for ded in old_ss.deductions:
			deduction = new_ss.append("deductions", {})
			deduction.salary_component = ded.salary_component
			deduction.amount_based_on_formula = 0
			deduction.is_tax_applicable = 0
			deduction.depends_on_payment_days = 0

			if _(ded.salary_component) == _(gosi_component):
				deduction.amount = gosi_amount
			else:
				deduction.amount = ded.amount

	new_ss.save(ignore_permissions=True)
	new_ss.add_comment('Comment', 'This Salary Structure is created on {0} for GOSI Deduction'.format(gosi_date))
	new_ss.submit()

	return new_ss.name


def create_salary_structure_assignment_for_gosi(employee, salary_structure, from_date):
	# print(from_date, "==========from_date===========")
	ss = frappe.get_doc("Salary Structure", salary_structure)
	total_monthly_salary = 0
	if len(ss.earnings)>0:
		for ear in ss.earnings:
			total_monthly_salary = total_monthly_salary + ear.amount
	
	assignment = frappe.new_doc("Salary Structure Assignment")
	assignment.employee = employee
	assignment.salary_structure = salary_structure
	assignment.from_date = getdate(from_date)
	assignment.base = total_monthly_salary
	assignment.custom_assignment_type = "GOSI"
	assignment.save(ignore_permissions=True)
	assignment.add_comment('Comment', 'This Salary Structure Assignment is created on {0} for GOSI Deduction'.format(from_date))
	assignment.submit()

def create_additional_salary_for_gosi(employee, payroll_date, gosi_component, gosi_amount):
	additional_salary = frappe.new_doc("Additional Salary")
	additional_salary.employee = employee
	additional_salary.payroll_date = payroll_date
	additional_salary.salary_component =  gosi_component
	additional_salary.overwrite_salary_structure_amount = 1
	additional_salary.amount = gosi_amount
	additional_salary.custom_additional_salary_type = "GOSI"
	additional_salary.save(ignore_permissions=True)
	additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for GOSI Deduction'.format(payroll_date))
	additional_salary.submit()

@frappe.whitelist()
def create_new_gosi_based_salary_for_eligible_employee(gosi_date=None):
	# print(gosi_date, "=================date==============")
	if not gosi_date:
		gosi_date = getdate(nowdate())

	stats_settings = frappe.get_doc('Stats Settings ST')
	gosi_percentage = None
	new_gosi_start_date = None

	if len(stats_settings.gosi_deduction_increment_details) > 0:
		date_for_gosi = add_to_date(gosi_date, days=5)

		for gosi in stats_settings.gosi_deduction_increment_details:
			if getdate(date_for_gosi) >= getdate(gosi.from_date) and getdate(date_for_gosi) <= getdate(gosi.to_date):
				gosi_percentage = gosi.deduction_percentage
				new_gosi_start_date = gosi.from_date
				break

	# print(gosi_percentage,"===========gosi_percentage==========")
	# print(new_gosi_start_date, "================new_gosi_start_date====================")

	if gosi_percentage:
		employee_list = frappe.db.sql_list("SELECT emp.name FROM `tabEmployee` as emp WHERE emp.status = 'Active' AND emp.custom_gosi_type = 'Vary'")
		# print(employee_list, "=========employee_list=============")

		if len(employee_list) > 0:
			for emp in employee_list:
				gosi_component, gosi_formula = None, None
				gosi_component_details = get_gosi_deduction_compenent_formula_and_name(emp)
				if len(gosi_component_details) > 0:
					gosi_component = gosi_component_details['gosi_component']
					gosi_formula = gosi_component_details['gosi_formula']

					emp_salary_assigment = get_latest_salary_structure_assignment(emp, gosi_date)
					# print(emp_salary_assigment, "==============emp_salary_assigment============")
					if emp_salary_assigment:
						salary_structure = frappe.db.get_value("Salary Structure Assignment", emp_salary_assigment, "salary_structure")
						new_gosi_deduction_amount, old_gosi_deduction_amount = get_gosi_deduction_amount(salary_structure, gosi_formula, gosi_component, gosi_percentage)

						gosi_additional_salary_amount = 0
						old_gosi_days = getdate(new_gosi_start_date).day - 1
						new_gosi_days = 30 - old_gosi_days

						if old_gosi_days > 0:
							gosi_additional_salary_amount = (old_gosi_days * (old_gosi_deduction_amount / 30)) + (new_gosi_days * (new_gosi_deduction_amount / 30))
						# print(gosi_additional_salary_amount, "============gosi_additional_salary_amount===============")
					
						### check for existing salary structure with new gosi percentage
						existing_ss = frappe.get_all("Salary Structure", filters={"custom_employee_no": emp, "custom_type_of_creation": "GOSI", "name": ["like", "%/GOSI-" + cstr(gosi_percentage)]}, pluck="name")

						existing_additional_salary = frappe.get_all("Additional Salary", filters={"employee": emp, "custom_additional_salary_type": "GOSI", "salary_component": gosi_component, "overwrite_salary_structure_amount": 1}, pluck="name")
						
						# print(existing_ss, "===========existing_ss============")
						if len(existing_ss) == 0:
							if new_gosi_deduction_amount != old_gosi_deduction_amount:
								### create new salary structure with new gosi amount
								new_salary_structure = create_salary_structure_for_gosi(salary_structure, emp, gosi_component, new_gosi_deduction_amount, gosi_percentage, gosi_date)

								### create salary structure assignment for new salary structure
								create_salary_structure_assignment_for_gosi(emp, new_salary_structure, gosi_date)

						if len(existing_additional_salary) == 0 and gosi_additional_salary_amount > 0:
								### create additional salary for gosi deduction
								create_additional_salary_for_gosi(emp, gosi_date, gosi_component, gosi_additional_salary_amount)