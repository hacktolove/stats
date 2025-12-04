# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff,today,get_link_to_form, cint, flt, add_to_date
from stats.stats.report.employee_attendance.employee_attendance import execute
from stats.hr_utils import get_latest_total_monthly_salary_of_employee, get_no_of_day_between_dates
from erpnext.setup.doctype.employee.employee import is_holiday
from stats.salary import get_latest_salary_structure_assignment, get_latest_basic_salary_of_employee


class OvertimeSheetST(Document):
	
	def validate(self):
		self.calculate_amount_based_on_actual_extra_hours_and_set_total_amount()
		self.validate_start_date_and_end_date()
		# self.create_payment_request_on_submit_of_ot_sheet()
	
	def on_submit(self):
		self.create_payment_request_on_submit_of_ot_sheet()

	def calculate_amount_based_on_actual_extra_hours_and_set_total_amount(self):
		total_due_amt = 0
		if len(self.overtime_sheet_employee_details)>0:
			for row in self.overtime_sheet_employee_details:
				overtime_start_date = frappe.db.get_value("Overtime Request ST",row.overtime_request_reference,"overtime_start_date")
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
								rate_per_hour = flt(((monthly_salary or 0)/(30 * per_day_hour)),2)
								basic_salary = get_latest_basic_salary_of_employee(row.employee_no,overtime_start_date)
								row.basic_salary = round(basic_salary,2)	

								### Overtime Rate Per Hour Formula --> (50 % of per hour basic salary) + per hour total salary
								basic_rate_per_hour = flt((basic_salary or 0)/(30 * per_day_hour),2)
								print(basic_rate_per_hour, '---basic rate per hour')
								extra_basic_amount = flt((basic_rate_per_hour * (percentage_for_overtime/100)), 2)
								overtime_rate_per_hour = flt(extra_basic_amount + rate_per_hour, 2)

								# truncated_overtime_rate_per_hour = math.trunc(overtime_rate_per_hour*100.0)/100.0
								# print(truncated_overtime_rate_per_hour, '---truncated overtime rate per hour')
								
								row.due_amount_per_hour = overtime_rate_per_hour
								# row.extra_amount_of_basic_salary = extra_basic_amount
								# row.overtime_rate_per_hour = overtime_rate_per_hour
								row.amount = flt((flt(row.actual_extra_hours) or 0) * overtime_rate_per_hour , 2)

								print(row.amount, '---row.due_amount')
						else :
							frappe.throw(_("Please set percentage for overtime in stats settings."))
					elif contract_actual_type and contract_actual_type == "Civil":
						monthly_salary = get_latest_total_monthly_salary_of_employee(row.employee_no)
						per_day_hour = frappe.db.get_value("Contract Type ST",employee_contract_type,"total_hours_per_day")
						rate_per_hour = flt(((monthly_salary or 0)/(30 * per_day_hour)),2)
						basic_salary = get_latest_basic_salary_of_employee(row.employee_no,overtime_start_date)
						row.basic_salary = round(basic_salary,2)
						transportation_amount = 0
						multiplication_factor_for_basic_salary = frappe.db.get_single_value("Stats Settings ST","multiplication_factor_of_overtime_for_civil_contract")
						print("--------------------", multiplication_factor_for_basic_salary)
						transportation_component = frappe.db.get_single_value("Stats Settings ST","overtime_transportation_earning_component")
						if cint(multiplication_factor_for_basic_salary)>0:
							overtime_rate_per_hour = flt(basic_salary / cint(multiplication_factor_for_basic_salary), 2)
							# truncated_overtime_rate_per_hour = math.trunc(overtime_rate_per_hour*100.0)/100.0
							
							latest_salary_structure_assignment = get_latest_salary_structure_assignment(row.employee_no,overtime_start_date)
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
							row.due_amount_per_hour = overtime_rate_per_hour
							row.amount = flt((overtime_rate_per_hour * (flt(row.actual_extra_hours) or 0)),2) + flt((transportation_amount_per_day * (row.total_no_of_approved_days or 0)),2)
						else:
							frappe.throw(_("Please set multiplication factor for overtime in stats settings."))
				else:
					frappe.throw(_("Please set contract type in Employee {0}".format(get_link_to_form("Employee",row.employee_no))))
				total_due_amt = total_due_amt + (row.amount or 0)

		self.total_amount = total_due_amt
	
	def validate_start_date_and_end_date(self):
		if self.from_date and self.to_date:
			if self.to_date < self.from_date:
				frappe.throw(_("End date can not be less than Start date"))

	def create_payment_request_on_submit_of_ot_sheet(self):

		company = erpnext.get_default_company()
		company_default_overtime_budget_expense_account = frappe.db.get_value("Company",company,"custom_overtime_budget_expense_account")
		pr_doc = frappe.new_doc("Payment Request ST")
		pr_doc.date = today()
		pr_doc.reference_name = "Overtime Sheet ST"
		pr_doc.reference_no = self.name
		pr_doc.budget_account = company_default_overtime_budget_expense_account
		pr_doc.party_type = "Employee"
		pr_doc.type = "Classified"
		
		if len(self.overtime_sheet_employee_details)>0:
			for row in self.overtime_sheet_employee_details:
				pr_row = pr_doc.append("employees",{})
				pr_row.employee_no = row.employee_no
				pr_row.amount = row.amount

		pr_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Request {0} is created").format(get_link_to_form("Payment Request ST", pr_doc.name)),alert=1)

	@frappe.whitelist()
	def fetch_employees_from_overtime_request(self):
		final_overtime_employee_list = []
		filters = {"docstatus":1,"status":"Completed","overtime_start_date":["between",[self.from_date,self.to_date]],"overtime_end_date":["between",[self.from_date,self.to_date]]}

		if self.main_department:
			filters["main_department"]=self.main_department
		if self.sub_department:
			filters["sub_department"]=self.sub_department

		overtime_employee_list = frappe.db.get_all("Overtime Request ST",
											 filters=filters,
											 fields=["name"])
		print(overtime_employee_list,"overtime_employee_list ==============")
		overtime_sheet_list = frappe.db.get_all("Overtime Sheet Employee Details ST",fields=["overtime_request_reference"])
		final_overtime_request_list = []
		for overtime_request in overtime_employee_list:
			found=False
			if len(overtime_sheet_list)>0:
				for ele in overtime_sheet_list:
					if ele.overtime_request_reference == overtime_request.name:
						found=True
						break
			if found==False:
				overtime_approval_request = frappe.db.exists("Overtime Approval Request ST", {"overtime_reference":overtime_request.name,"docstatus":1})
				if overtime_approval_request:
					final_overtime_request_list.append(overtime_request)
		print(final_overtime_request_list,"final_overtime_request_list **************")
		if len(final_overtime_request_list)>0:
			for overtime in final_overtime_request_list:
				print(final_overtime_request_list,"final_overtime_request_list ==============")
				overtime_request_doc = frappe.get_doc("Overtime Request ST",overtime.name)
				if len(overtime_request_doc.employee_overtime_request)>0:
					overtime_days = overtime_request_doc.total_no_of_days
					for row in overtime_request_doc.employee_overtime_request:
						if row.request_status == "Accepted":
							overtime_employee_details = {}
							print(overtime_request_doc.name,"---------- overtime_request_doc ---------------")
							overtime_employee_details["employee_no"]=row.employee_no
							overtime_employee_details["employee_name"]=row.employee_name
							overtime_employee_details["request_date"]=overtime_request_doc.creation_date
							overtime_employee_details["overtime_request_reference"]=overtime_request_doc.name
							overtime_employee_details["no_of_hours_per_day"]=row.no_of_hours_per_day
							required_extra_hours = flt(row.no_of_hours_per_day) * overtime_days
							overtime_employee_details["required_extra_hours"]=required_extra_hours
							overtime_employee_details["required_days"]=overtime_days
							overtime_approval_doc = frappe.db.get_value("Overtime Approval Request ST",{"docstatus":1,"overtime_reference":overtime_request_doc.name},"name")
							no_of_vacation_days = frappe.db.get_value("Overtime Approval Employee Details ST",{"parent":overtime_approval_doc,"docstatus":1,"employee_no":row.employee_no},"no_of_vacation")
							no_of_absent_days = frappe.db.get_value("Overtime Approval Employee Details ST",{"parent":overtime_approval_doc,"docstatus":1,"employee_no":row.employee_no},"no_of_absent")
							# get approved days from overtime approval employee details
							approved_days = frappe.db.get_value("Overtime Approval Employee Details ST",{"parent":overtime_approval_doc,"docstatus":1,"employee_no":row.employee_no},"approved_days")
							# overtime_employee_details["approved_days"]=approved_days or 0
							overtime_employee_details["transportation_amount"]= row.transportation_amount or 0
							overtime_employee_details["transport_per_day"]= row.transport_per_day or 0
							overtime_employee_details['basic_salary']=row.basic_salary
							overtime_employee_details['due_amount_per_hour'] = row.overtime_rate_per_hour
							overtime_employee_details['total_salary'] = flt(row.total_salary,2)

							# no_of_vacation_days = 0
							# if overtime_request_doc.day_type == "Week Days":
							# 	leave_application_list = frappe.db.get_all("Leave Application",
							# 				filters={"employee":row.employee_no,"docstatus":1},
							# 				or_filters={"from_date":["between",[overtime_request_doc.overtime_start_date,overtime_request_doc.overtime_end_date]],"to_date":["between",[overtime_request_doc.overtime_start_date,overtime_request_doc.overtime_end_date]]},
							# 				fields=["name"])
							# 	if len(leave_application_list)>0:
							# 		for la in leave_application_list:
							# 			leave = frappe.get_doc("Leave Application",la.name)
							# 			no_of_vacation_days = no_of_vacation_days + get_no_of_day_between_dates(overtime_request_doc.overtime_start_date,overtime_request_doc.overtime_end_date,leave.from_date,leave.to_date,row.employee_no)
											
							# 	leave_outside_overtime_list = frappe.db.get_all("Leave Application",
							# 				filters={"employee":row.employee_no,"docstatus":1,"from_date":["<",overtime_request_doc.overtime_start_date],"to_date":[">",overtime_request_doc.overtime_end_date]},
							# 				fields=["name"])
							# 	if len(leave_outside_overtime_list)>0:
							# 		for ola in leave_outside_overtime_list:
							# 			leave_doc = frappe.get_doc("Leave Application",ola.name)
							# 			no_of_vacation_days = no_of_vacation_days + get_no_of_day_between_dates(overtime_request_doc.overtime_start_date,overtime_request_doc.overtime_end_date,leave_doc.from_date,leave_doc.to_date,row.employee_no)

							# else:
							# 	no_of_vacation_days = 0
							
							# no_of_absent_days = 0
							# # get no of absent days from attendance
							# attendance_list = frappe.db.get_all("Attendance",
							# 				filters={"employee":row.employee_no,"docstatus":1,"attendance_date":["between",[overtime_request_doc.overtime_start_date,overtime_request_doc.overtime_end_date]],"status":"Absent"},
							# 				fields=["count(name) as total_absent_days"])
							# if attendance_list[0].total_absent_days and attendance_list[0].total_absent_days > 0:
							# 	no_of_absent_days = no_of_absent_days + attendance_list[0].total_absent_days
							overtime_employee_details["no_of_vacation"] = no_of_vacation_days or 0
							overtime_employee_details["no_of_absent"] = no_of_absent_days or 0
							overtime_employee_details["total_no_of_approved_days"] = approved_days

						# calculate actual extra hours based on attendance report

							# filters_for_report = frappe._dict({"employee":row.employee_no,"from_date":overtime_request_doc.overtime_start_date,"to_date":overtime_request_doc.overtime_end_date})
							# print(filters_for_report,"filters_for_report +++++++++++++++++++")
							# data_from_report = execute(filters_for_report,msgprint=0)
							# print(data_from_report[1],"-----------------------------------")
							# total_actual_extra_mins = 0
							# for record in data_from_report[1]:
							# 	if record.extra_minutes and record.extra_minutes >= 0:
							# 		print(record.extra_minutes,"=============record.extra_minutes")
							# 		total_actual_extra_mins = total_actual_extra_mins + record.extra_minutes
							# total_actual_extra_hours = total_actual_extra_mins / 60
							total_actual_extra_hours = flt(row.no_of_hours_per_day) * (approved_days or 0)
							overtime_employee_details["actual_extra_hours"]=total_actual_extra_hours
							amount = ((total_actual_extra_hours or 0) * (row.overtime_rate_per_hour or 0)) + ((approved_days or 0) * (row.transport_per_day))
							print(amount, "amount",total_actual_extra_hours,"<---total_actual_extra_hours",row.overtime_rate_per_hour,"<---row.overtime_rate_per_hour",approved_days,"<---approved_days",row.transport_per_day,"<---row.transport_per_day" )
							overtime_employee_details["amount"]=amount
							overtime_employee_details["overtime_rate_per_hour"]=row.overtime_rate_per_hour

							final_overtime_employee_list.append(overtime_employee_details)

		print(final_overtime_employee_list,"+   "*10)
		# for r in final_overtime_employee_list:
		# 	self.append("overtime_sheet_employee_details",r)
		return final_overtime_employee_list

