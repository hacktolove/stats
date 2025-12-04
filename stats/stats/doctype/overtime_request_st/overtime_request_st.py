# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from stats.hr_utils import (check_if_holiday_between_applied_dates, 
							check_employee_in_scholarship, check_employee_in_training, 
							check_available_amount_for_budget,
							get_latest_total_monthly_salary_of_employee,
							get_no_of_day_between_dates)
from frappe.utils import date_diff, flt, get_link_to_form, add_to_date, cint
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
from frappe.model.mapper import get_mapped_doc
from stats.salary import get_latest_salary_structure_assignment, get_latest_basic_salary_of_employee
import math

class OvertimeRequestST(Document):
	def validate(self):
		self.validate_overtime_dates()
		self.calculate_total_no_of_days_based_on_day_type()
		self.calculate_employee_due_amount()
		self.calculate_total_no_of_hours_and_employees()
		# self.validate_budget_for_overtime()
		self.calculate_total_salary()

	def on_submit(self):
		self.validate_status()
		# self.validate_budget_for_overtime()

	def validate_overtime_dates(self):
		if self.overtime_start_date and self.overtime_end_date and self.overtime_start_date > self.overtime_end_date:
			frappe.throw(_("Overtime start date cannot be greater than overtime end date"))
	
	def calculate_total_no_of_days_based_on_day_type(self):
		company = erpnext.get_default_company()
		actual_no_of_days = 0
		no_of_days = date_diff(self.overtime_end_date, self.overtime_start_date)+1
		default_holiday_list = frappe.db.get_value("Company",company, "default_holiday_list")
		if default_holiday_list:
			if self.day_type:
				if self.day_type == "Week Days":
					for day in range(no_of_days):
						request_date = add_to_date(self.overtime_start_date,days=day)
						holiday = is_holiday(default_holiday_list, date=request_date)
						if holiday == False:
							actual_no_of_days = actual_no_of_days + 1
				elif self.day_type == "Off-Days":
					for day in range(no_of_days):
						request_date = add_to_date(self.overtime_start_date,days=day)
						holiday = is_holiday(default_holiday_list, date=request_date)
						if holiday == True:
							actual_no_of_days = actual_no_of_days + 1
		else:
			frappe.throw(_("Please set default holiday list in company {0}".format(get_link_to_form("Company",company))))
		
		self.total_no_of_days = actual_no_of_days
	
	def calculate_total_no_of_hours_and_employees(self):
		total_no_of_hour = 0
		total_no_of_employee = 0
		if len(self.employee_overtime_request)>0:
			for row in self.employee_overtime_request:
				if row.no_of_hours_per_day:
					total_no_of_hour = total_no_of_hour + (flt(row.no_of_hours_per_day) * self.total_no_of_days)
					total_no_of_employee = total_no_of_employee + 1
		
		self.total_no_of_hours = total_no_of_hour
		self.total_no_of_employees = total_no_of_employee


	def calculate_employee_due_amount(self):
		total_due_amt = 0
		if len(self.employee_overtime_request) > 0:
			no_of_day = date_diff(self.overtime_end_date, self.overtime_start_date)+1
			
			for row in self.employee_overtime_request:
				employee_contract_type = frappe.db.get_value("Employee",row.employee_no,"custom_contract_type")
				if employee_contract_type:
					contract_actual_type = frappe.db.get_value("Contract Type ST",employee_contract_type,"contract")
					print(contract_actual_type, '---contract_actual_type')
					if contract_actual_type and contract_actual_type == "Direct":
						print("IN DIRECT CONTRACT")
						percentage_for_overtime = frappe.db.get_single_value("Stats Settings ST","percentage_for_overtime")
						if percentage_for_overtime:
							monthly_salary = get_latest_total_monthly_salary_of_employee(row.employee_no)
							# per_day_salary = ((monthly_salary or 0)/30)
							per_day_hour = None
							if employee_contract_type:
								per_day_hour = frappe.db.get_value("Contract Type ST",employee_contract_type,"total_hours_per_day")
								row.rate_per_hour = flt(((monthly_salary or 0)/(30 * per_day_hour)),2)
								basic_salary = get_latest_basic_salary_of_employee(row.employee_no,self.overtime_start_date)
								row.basic_salary = round(basic_salary,2)	

								### Overtime Rate Per Hour Formula --> (50 % of per hour basic salary) + per hour total salary
								basic_rate_per_hour = flt((basic_salary or 0)/(30 * per_day_hour),2)
								print(basic_rate_per_hour, '---basic rate per hour')
								extra_basic_amount = flt((basic_rate_per_hour * (percentage_for_overtime/100)), 2)
								overtime_rate_per_hour = flt(extra_basic_amount + row.rate_per_hour, 2)

								# print(overtime_rate_per_hour, '---overtime rate per hour',(basic_rate_per_hour * (percentage_for_overtime/100)) + row.rate_per_hour )
								# truncated_overtime_rate_per_hour = math.trunc(overtime_rate_per_hour*100.0)/100.0
								# print(truncated_overtime_rate_per_hour, '---truncated overtime rate per hour')

								row.extra_amount_of_basic_salary = extra_basic_amount
								row.overtime_rate_per_hour = overtime_rate_per_hour
								row.due_amount = flt((flt(row.no_of_hours_per_day) or 0) * (row.total_no_of_days or 0) * overtime_rate_per_hour , 2)
								# print(row.rate_per_hour,row.overtime_rate_per_hour,row.no_of_hours_per_day,no_of_day,row.due_amount,"============",(flt(row.no_of_hours_per_day) or 0) * (row.total_no_of_days or 0) * overtime_rate_per_hour )
								
								print(row.due_amount, '---row.due_amount')
						else :
							frappe.throw(_("Please set percentage for overtime in stats settings."))
					elif contract_actual_type and contract_actual_type == "Civil":
						monthly_salary = get_latest_total_monthly_salary_of_employee(row.employee_no)
						per_day_hour = frappe.db.get_value("Contract Type ST",employee_contract_type,"total_hours_per_day")
						row.rate_per_hour = flt(((monthly_salary or 0)/(30 * per_day_hour)),2)
						basic_salary = get_latest_basic_salary_of_employee(row.employee_no,self.overtime_start_date)
						row.basic_salary = round(basic_salary,2)
						transportation_amount = 0
						multiplication_factor_for_basic_salary = frappe.db.get_single_value("Stats Settings ST","multiplication_factor_of_overtime_for_civil_contract")
						print("--------------------", multiplication_factor_for_basic_salary)
						transportation_component = frappe.db.get_single_value("Stats Settings ST","overtime_transportation_earning_component")
						if cint(multiplication_factor_for_basic_salary)>0:
							overtime_rate_per_hour = flt(basic_salary / cint(multiplication_factor_for_basic_salary), 2)
							# truncated_overtime_rate_per_hour = math.trunc(overtime_rate_per_hour*100.0)/100.0
							row.overtime_rate_per_hour = overtime_rate_per_hour
							latest_salary_structure_assignment = get_latest_salary_structure_assignment(row.employee_no,self.overtime_start_date)
							if latest_salary_structure_assignment:
								latest_salary_structure = frappe.db.get_value("Salary Structure Assignment",latest_salary_structure_assignment,"salary_structure")
								if latest_salary_structure:
									salary_structure_doc = frappe.get_doc("Salary Structure",latest_salary_structure)
									if len(salary_structure_doc.earnings)>0:
										found = False
										for earning_row in salary_structure_doc.earnings:
											if transportation_component:
												if earning_row.salary_component == transportation_component:
													found = True
													transportation_amount = earning_row.amount
													break
											else:
												frappe.throw(_("Please set Transportation Earning Component in stats settings."))
										if found == False:
											frappe.msgprint(_("Transportation Earning Component {0} is not found in {1} salary structure of employee {2}".format(transportation_component,latest_salary_structure,row.employee_no)),alert=1)
							transportation_amount_per_day = flt(transportation_amount / 30 , 2)
							# truncated_transportation_amount_per_day = math.trunc(transportation_amount_per_day*100.0)/100.0
							row.transport_per_day = transportation_amount_per_day
							row.due_amount = flt((overtime_rate_per_hour * (flt(row.no_of_hours_per_day) or 0) * (row.total_no_of_days or 0)),2) + flt((transportation_amount_per_day * (row.total_no_of_days or 0)),2)
						else:
							frappe.throw(_("Please set multiplication factor for overtime in stats settings."))
				else:
					frappe.throw(_("Please set contract type in Employee {0}".format(get_link_to_form("Employee",row.employee_no))))
				total_due_amt = total_due_amt + (row.due_amount or 0)
			
		print(total_due_amt,"===========================================================================")
		self.total_due_amount = total_due_amt
	def validate_status(self):
		pending = False
		# if self.status:
		# 	if self.status == None or self.status == "Pending":
		# 		frappe.throw(_("Please Approve or Reject overtime request before submit"))
		if len(self.employee_overtime_request)>0:
			for row in self.employee_overtime_request:
				if row.request_status in ["Pending","",None]:
					pending = True
					frappe.throw(_("Row #{0}: Please select Accept or Reject".format(row.idx)))
		if pending == False:
			frappe.db.set_value(self.doctype,self.name,"status","Completed")
	

	def validate_budget_for_overtime(self):
		if self.total_due_amount:
			company = erpnext.get_default_company()
			budget_account = frappe.db.get_value("Company", company, "custom_overtime_budget_expense_account")
			cost_center = frappe.db.get_value("Department", self.main_department, "custom_department_cost_center")

			budget = check_available_amount_for_budget(budget_account,cost_center)
			print(budget, '--busget')
			if budget:
				if self.total_due_amount > budget:
					frappe.throw(_("Total Due amount {0} can't be greater than Budget Amount: {1}").format(self.total_due_amount, budget))
			else:
				frappe.throw(_("No budget found for your department"))

	def calculate_total_salary(self):
		if len(self.employee_overtime_request) > 0:
			for row in self.employee_overtime_request:
				total = 0
				transportation_amount = 0
				latest_salary_structure_assignment = get_latest_salary_structure_assignment(row.employee_no,self.overtime_start_date)
				if latest_salary_structure_assignment:
					latest_salary_structure = frappe.db.get_value("Salary Structure Assignment",latest_salary_structure_assignment,"salary_structure")
					if latest_salary_structure:
						salary_structure_doc = frappe.get_doc("Salary Structure",latest_salary_structure)
						transportation_component = frappe.db.get_single_value("Stats Settings ST","overtime_transportation_earning_component")
						if len(salary_structure_doc.earnings)>0:
							for d in salary_structure_doc.earnings:
								if transportation_component:
									if d.salary_component == transportation_component:
										transportation_amount = d.amount
								total = total + d.amount
							row.total_salary = flt(total,2)
							row.transportation_amount = transportation_amount
	@frappe.whitelist()
	def get_employee(self):
		emp = {}
		emp_list=[]
		filters = {"status":"Active", "department":self.main_department}
		if self.sub_department:
			filters["custom_sub_department"]=self.sub_department
		employee_list = frappe.db.get_all("Employee", filters=filters, fields=["name","employee_name","custom_contract_type"])
		if len(employee_list) > 0:
			for employee in employee_list:
				scholarship = check_employee_in_scholarship(employee.name,self.overtime_start_date, self.overtime_end_date)
				training = check_employee_in_training(employee.name,self.overtime_start_date, self.overtime_end_date)
				# holiday = check_if_holiday_between_applied_dates(employee.name, self.overtime_start_date, self.overtime_end_date)
				# print(holiday,"--------------------")
				# print(scholarship, '--scholarship', training, '--training', holiday, '--holiday', employee.name)
				if scholarship == True:
					print(employee.name, '==scholarship')
					frappe.msgprint(_("Employee {0} is applied for scholarship").format(employee.name), alert=1)
					continue
				if training == True:
					print(employee.name, '==training')
					frappe.msgprint(_("Employee {0} is in training").format(employee.name), alert=1)
					continue
				# print(holiday, flt(date_diff(self.overtime_end_date, self.overtime_start_date) + 1), '==================')
				# if holiday !=  flt(date_diff(self.overtime_end_date, self.overtime_start_date)):
				# if holiday == True:
				# 	print(employee.name, '==holiday')
				# 	frappe.msgprint(_("Employee {0} has holiday during overtime request dates").format(employee.name), alert=1)
				# 	continue
				not_eligible_for_overtime = frappe.db.get_value("Contract Type ST",employee.custom_contract_type,"not_eligible_for_overtime")
				if not_eligible_for_overtime==1:
					frappe.msgprint(_("Employee {0} is not eligible for Overtime based on Contract Type {1}").format(employee.name,get_link_to_form("Contract Type ST",employee.custom_contract_type)), alert=1)
					continue

				emp["employee_no"]=employee.name
				emp["employee_name"]=employee.employee_name
				emp_list.append(emp.copy())
					# print(emp, '--for dict')

		print(emp, '---dict')
		return emp_list

@frappe.whitelist()
def create_overtime_approval_request(source_name):
	overtime_doc = frappe.get_doc("Overtime Request ST",source_name)
	
	overtime_approval_doc = frappe.new_doc("Overtime Approval Request ST")
	overtime_approval_doc.overtime_reference=source_name
	if len(overtime_doc.employee_overtime_request)>0:
		for row in overtime_doc.employee_overtime_request:
			overtime_approval_doc.append("overtime_approval_employee_details",{"employee_no":row.employee_no,"total_no_of_days":row.total_no_of_days})

	overtime_approval_doc.flags.ignore_mandatory = True
	overtime_approval_doc.save()	
	
	return overtime_approval_doc.name
