# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, add_to_date, get_datetime, get_date_str, cstr, get_first_day, get_last_day, getdate, time_diff_in_hours, get_link_to_form
from stats.hr_utils import check_if_holiday_between_applied_dates
from stats.salary import get_latest_salary_structure_assignment


class ScholarshipRequestsProcessingST(Document):
	def on_submit(self):
		if len(self.scholarship_request_details)>0:
			for row in self.scholarship_request_details:
				if row.action == "Open":
					frappe.throw(_("You cannot submit.<br>Please Accept or Reject Scholarship Request {0} in row {1}").format(row.scholarship_request_reference,row.idx))
				
		self.create_future_attendance_for_scholarship_time()
		self.create_salary_structure_for_start_date_of_month()
		self.create_salary_structure_for_other_than_start_date_of_month()
		self.change_scholarship_request_status_and_set_scholarship_start_end_date()

	def change_scholarship_request_status_and_set_scholarship_start_end_date(self):
		if len(self.get("scholarship_request_details")) > 0:
			for item in self.get("scholarship_request_details"):
				scholarship_request_doc = frappe.get_doc("Scholarship Request ST",item.scholarship_request_reference)
				if scholarship_request_doc.acceptance_status != item.action:
					scholarship_request_doc.acceptance_status = item.action
					scholarship_request_doc.scholarship_start_date = self.scholarship_start_date
					scholarship_request_doc.scholarship_end_date = self.scholarship_end_date
					frappe.msgprint(_("Status of {0} is changed to {1}").format(get_link_to_form("Scholarship Request ST", scholarship_request_doc.name),item.action),alert=1)
					scholarship_request_doc.save(ignore_permissions=True)

	def create_future_attendance_for_scholarship_time(self):
		if len(self.scholarship_request_details)> 0:
			days = date_diff(self.scholarship_end_date,self.scholarship_start_date)
			permission_days = frappe.db.get_value("Scholarship ST",{"scholarship_no":self.scholarship_no},"permission_days")
			if permission_days and permission_days > 0:
				days = days + permission_days
			
			last_attendance_date = None
			different_years_list = []
			for fiscal_year in range ((self.scholarship_start_date).year, (self.scholarship_end_date).year+1):
				if fiscal_year not in different_years_list:
					different_years_list.append(fiscal_year)

			yearly_holiday_list = []

			for year in different_years_list:
				holiday = {}
				fiscal_year_doc = frappe.get_doc("Fiscal Year",year)
				exist_holiday_list = frappe.db.get_all("Holiday List",
											filters={"to_date":fiscal_year_doc.year_end_date,"from_date":fiscal_year_doc.year_start_date},
											fields=["name"])
				if len(exist_holiday_list)<1:
					frappe.throw(_("Holiday list for year <b>{0}</b> does not exists. Hence we cannot create future attendance.").format(year))
				else :
					holiday["year"]=year
					holiday["holiday_list"]=exist_holiday_list[0].name
					yearly_holiday_list.append(holiday)

			for day in range (days+1):
				attendance_date = add_to_date(self.scholarship_start_date,days=day)
				
				for row in self.scholarship_request_details:
					if row.action == "Accepted":
						check_holiday = None
						for ele in yearly_holiday_list:
							if attendance_date.year == ele.get("year"):
								check_holiday = check_if_holiday_between_applied_dates(row.employee_no,attendance_date,attendance_date,holiday_list=ele.get("holiday_list"))
						
						if check_holiday == False:
							attendance_doc = frappe.new_doc("Attendance")
							attendance_doc.employee = row.employee_no
							attendance_doc.attendance_date = attendance_date
							attendance_doc.custom_attendance_type = "Scholarship"

							employee_shift = frappe.db.get_value("Employee",row.employee_no,"default_shift")
							shift_start_time = frappe.db.get_value("Shift Type",employee_shift,"start_time")
							shift_end_time = frappe.db.get_value("Shift Type",employee_shift,"end_time")

							in_time = get_datetime(get_date_str(attendance_date) + " " + cstr(shift_start_time))
							out_time = get_datetime(get_date_str(attendance_date) + " " + cstr(shift_end_time))
							total_working_hours = time_diff_in_hours(in_time, out_time)

							attendance_doc.shift = employee_shift
							attendance_doc.in_time = in_time
							attendance_doc.out_time = out_time
							attendance_doc.working_hours = total_working_hours
							attendance_doc.status = "Present"
							attendance_doc.save(ignore_permissions=True)
							attendance_doc.submit()
							last_attendance_date = attendance_date
			frappe.msgprint(_("Attendance from {0} to {1} is created.").format(self.scholarship_start_date,last_attendance_date),alert=True)

	def create_salary_structure_for_start_date_of_month(self):
		if len(self.scholarship_request_details)> 0:
			for row in self.scholarship_request_details:
				if row.action == "Accepted":
					future_salary_assignment = frappe.db.get_all("Salary Structure Assignment",
														fields=["name"],
														filters={"from_date": [">=", self.scholarship_start_date],
															"employee": row.employee_no, "docstatus":1}, limit=1)
					print(future_salary_assignment, '--future_salary_assignment')
					if len(future_salary_assignment) > 0:
						doc = frappe.get_doc("Salary Structure Assignment", future_salary_assignment[0].name)
						doc.cancel() 
						frappe.msgprint(_("Salary Structure Assignment {0} Cancelled.").format(future_salary_assignment[0].name),alert=1)

					print("*******************************")
					latest_salary_structure = frappe.db.get_all("Salary Structure", 
													fields=["custom_employee_no", "name"],
													filters={"custom_employee_no": row.employee_no, "docstatus":1}, limit=1)
					print(latest_salary_structure, '---latest_salary_structure')
					if len(latest_salary_structure) > 0:
						prev_ss = frappe.get_doc("Salary Structure", latest_salary_structure[0].name)
						# print(get_first_day(self.scholarship_start_date)== getdate(self.scholarship_start_date),'-----get_first_day(self.scholarship_start_date)s')
						if get_first_day(self.scholarship_start_date) == getdate(self.scholarship_start_date):

							new_ss = frappe.copy_doc(prev_ss)
							new_ss.__newname = row.employee_no + "/" + self.name
							new_ss.name = row.employee_no + "/" + self.name
							new_ss.custom_contract_start_date = self.scholarship_start_date

							grade = frappe.db.get_value('Employee', row.employee_no, 'grade')
							if grade == None:
								frappe.throw(_("Set Grade in employee profile."))
							
							basic_salary_component =frappe.db.get_value("Employee Grade", grade, 'custom_basic_salary_component')

							# basic_salary_component = frappe.db.get_single_value('Stats Settings ST', 'basic_salary_component')

							basic_ear = 0
							for row in prev_ss.earnings:
								if row.salary_component == basic_salary_component :
									basic_ear = row.amount
									break

							new_ss.earnings = []
							# new_ss.deductions = []
							ear = new_ss.append("earnings", {})
							ear.salary_component = basic_salary_component
							ear.amount = basic_ear * 0.5
							ear.amount_based_on_formula = 0
							ear.is_tax_applicable = 0

							new_ss.save(ignore_permissions=True)

							frappe.msgprint(_("Salary Structure {0} created.").format(new_ss.name), alert=1)

							new_ss.submit()
						
						######### create salary structure assignment

						if get_last_day(self.scholarship_end_date) == getdate(self.scholarship_end_date):
							if self.scholarship_end_date:
								total_monthly_salary = 0
								if len(prev_ss.earnings)>0:
									for ear in prev_ss.earnings:
										total_monthly_salary = total_monthly_salary + ear.amount

								next_month = add_to_date(self.scholarship_end_date,months=1)
								assignment = frappe.new_doc("Salary Structure Assignment")
								assignment.employee = row.employee_no
								assignment.salary_structure = prev_ss.name
								assignment.from_date = get_first_day(next_month)
								assignment.base = total_monthly_salary

								assignment.save(ignore_permissions=True)
								frappe.msgprint(_("Salary Structure Assignment {0} created." .format(assignment.name)), alert=True)
								assignment.submit()

	def create_salary_structure_for_other_than_start_date_of_month(self):
		if len(self.scholarship_request_details)> 0:
			for scholarship in self.scholarship_request_details:
				if scholarship.action == "Accepted":
					latest_salary_assignment = get_latest_salary_structure_assignment(scholarship.employee_no, getdate(self.scholarship_start_date))
					latest_salary_structure = frappe.db.get_all("Salary Structure", 
													fields=["custom_employee_no", "name"],
													filters={"custom_employee_no": scholarship.employee_no, "docstatus":1}, limit=1)
					print(latest_salary_structure, '---latest_salary_structure')
					print(latest_salary_assignment, '---latest_salary_assignment')

					if len(latest_salary_assignment) > 0:
						salary_structure = frappe.db.get_value("Salary Structure Assignment", latest_salary_assignment, "salary_structure")
						prev_ss = frappe.get_doc("Salary Structure", salary_structure)
						# print(get_first_day(self.scholarship_start_date), '-----get_first_day(self.scholarship_start_date)s')
						if get_first_day(self.scholarship_start_date) != getdate(self.scholarship_start_date):

							######### additonal salary for scholarship starting month
							for ear in prev_ss.earnings:
								additional_salary = frappe.new_doc('Additional Salary')
								additional_salary.employee = scholarship.employee_no
								additional_salary.payroll_date = self.scholarship_start_date
								additional_salary.salary_component =  ear.salary_component
								additional_salary.overwrite_salary_structure_amount = 1

								grade = frappe.db.get_value('Employee', scholarship.employee_no, 'grade')
								if grade == None:
									frappe.throw(_("Set Grade in employee profile."))
							
								basic_salary_component =frappe.db.get_value("Employee Grade", grade, 'custom_basic_salary_component')

								before_scholarship_days = (getdate(self.scholarship_start_date).day - 1)
								if ear.salary_component == basic_salary_component:
									end_date = get_last_day(self.scholarship_start_date).day - before_scholarship_days
									salary_before_scholarship = (before_scholarship_days * ear.amount) / 30
									salary_scholarship = (end_date * 0.5 * ear.amount) / 30
									additional_salary.amount = salary_before_scholarship + salary_scholarship
								else:
									additional_salary.amount = (before_scholarship_days * ear.amount) / 30

								additional_salary.save(ignore_permissions=True)
								frappe.msgprint(_("Additional Salary {0} Created").format(additional_salary.name), alert=1)
								additional_salary.submit()

							######### new salary structure for next month
							next_month_date = add_to_date(self.scholarship_start_date,months=1)

							new_ss = frappe.copy_doc(prev_ss)
							new_ss.__newname = scholarship.employee_no + "/" + self.name
							new_ss.name = scholarship.employee_no + "/" + self.name
							new_ss.custom_contract_start_date = get_first_day(next_month_date)
							new_ss.custom_employee_no = scholarship.employee_no

							# basic_salary_component = frappe.db.get_single_value('Stats Settings ST', 'basic_salary_component')

							grade = frappe.db.get_value('Employee', scholarship.employee_no, 'grade')
							if grade == None:
								frappe.throw(_("Set Grade in employee profile."))
						
							basic_salary_component =frappe.db.get_value("Employee Grade", grade, 'custom_basic_salary_component')

							basic_ear = 0
							for row in prev_ss.earnings:
								if row.salary_component == basic_salary_component :
									basic_ear = row.amount

							new_ss.earnings = []
							# new_ss.deductions = []
							earning = new_ss.append("earnings", {})
							earning.salary_component = basic_salary_component
							earning.amount = basic_ear * 0.5
							earning.amount_based_on_formula = 0
							earning.is_tax_applicable = 0

							new_ss.save(ignore_permissions=True)
							frappe.msgprint(_("Salary Structure {0} created.").format(new_ss.name), alert=1)
							new_ss.submit()


						if get_last_day(self.scholarship_end_date) != getdate(self.scholarship_end_date):

							######### additonal salary for scholarship ending month
							for ear in prev_ss.earnings:
								additional_salary = frappe.new_doc('Additional Salary')
								additional_salary.employee = scholarship.employee_no
								additional_salary.payroll_date = self.scholarship_end_date
								additional_salary.salary_component =  ear.salary_component
								additional_salary.overwrite_salary_structure_amount = 1

								# basic_salary_component = frappe.db.get_single_value('Stats Settings ST', 'basic_salary_component')
								# if basic_salary_component == None:
								# 	frappe.throw(_("Set Basic Salary Component in Stats Settings"))

								grade = frappe.db.get_value('Employee', scholarship.employee_no, 'grade')
								if grade == None:
									frappe.throw(_("Set Grade in employee profile."))
							
								basic_salary_component =frappe.db.get_value("Employee Grade", grade, 'custom_basic_salary_component')

								after_scholarship_days = (30 - getdate(self.scholarship_end_date).day)
								if ear.salary_component == basic_salary_component:
									scholarship_days = getdate(self.scholarship_end_date).day
									salary_scholarship = (scholarship_days * 0.5 * ear.amount) / 30
									salary_after_scholarship = (after_scholarship_days * ear.amount) / 30
									additional_salary.amount = salary_after_scholarship + salary_scholarship
								else:
									additional_salary.amount = (after_scholarship_days * ear.amount) / 30

								additional_salary.save(ignore_permissions=True)
								frappe.msgprint(_("Additional Salary {0} Created").format(additional_salary.name), alert=1)
								additional_salary.submit()

							######### create salary structure assignment form next month

							if self.scholarship_end_date:
								total_monthly_salary = 0
								if len(prev_ss.earnings)>0:
									for ear in prev_ss.earnings:
										total_monthly_salary = total_monthly_salary + ear.amount

								scholarship_end_next_month = add_to_date(self.scholarship_end_date,months=1)
								assignment = frappe.new_doc("Salary Structure Assignment")
								assignment.employee = scholarship.employee_no
								assignment.salary_structure = prev_ss.name
								assignment.from_date = get_first_day(scholarship_end_next_month)
								assignment.base = total_monthly_salary

								assignment.save(ignore_permissions=True)
								frappe.msgprint(_("Salary Structure Assignment {0} created." .format(assignment.name)), alert=True)
								assignment.submit()

	@frappe.whitelist()
	def get_scholarship_requests(self):
			
		filters={"docstatus":1,"acceptance_status": "Open","scholarship_no":self.scholarship_no}

		if self.from_date and self.to_date:
			filters["transaction_date"]=["between", [self.from_date, self.to_date]]
		if self.main_department:
			filters["main_department"]=self.main_department
		if self.sub_department:
			filters["sub_department"]=self.sub_department
		if self.specialisation_type:
			filters["specialisation_type"]=self.specialisation_type

		scholarship_request_list = frappe.db.get_all('Scholarship Request ST', filters=filters,fields=["name"],debug=1)

		if len(scholarship_request_list) < 1:
			frappe.msgprint(_("No data found"))

		return scholarship_request_list




@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_open_scholarships(doctype, txt, searchfield, start, page_len, filters):
	open_scholarships = frappe.db.get_all("Scholarship ST",
									   filters={"docstatus":1,"status":"Open","scholarship_no": ("like", f"{txt}%")},
									   fields=["scholarship_no"],as_list=1)
	return open_scholarships


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_specialisation_type_from_scholarship_no(doctype, txt, searchfield, start, page_len, filters):
	scholarship_no = filters.get("scholarship_no")
	scholarship_doc = frappe.get_doc("Scholarship ST",{"scholarship_no":scholarship_no})
	specialisation_type_list = frappe.db.get_all("Scholarship Details ST",
									   parent_doctype = "Scholarship ST",
									   filters={"parent":scholarship_doc.name,"specialisation_type": ("like", f"{txt}%")},
									   fields=["specialisation_type"],as_list=1)
	return specialisation_type_list