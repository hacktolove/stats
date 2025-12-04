# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import month_diff, today, getdate, add_to_date, cint
from frappe.model.document import Document


class EmployeeAlternativesST(Document):
	def validate(self):
		if len(self.employee_alternatives_details)>0:
			for emp in self.employee_alternatives_details:
				check_eployee_high_potential_record = frappe.db.get_all("High Performance Employee Details ST",
															filters={"employee_no":emp.get("employee_no"),"docstatus":1},
															fields=["name","employee_no","employee_psychometric_test_score","technical_evaluation"],order_by="modified desc")
				if len(check_eployee_high_potential_record)>0:
					emp.employee_psychometric_test_score = check_eployee_high_potential_record[0].employee_psychometric_test_score
					emp.technical_evaluation = check_eployee_high_potential_record[0].technical_evaluation
				else:
					emp.employee_psychometric_test_score = 0.0
					emp.technical_evaluation = 0.0
	
	@frappe.whitelist()
	def fetch_employees_based_on_filters(self):
		filters={"status":"Active"}
		if self.employee_main_department:
			filters["department"]=self.employee_main_department

		all_active_employee_list = frappe.db.get_all("Employee",
											   filters=filters,
											   fields=["name","date_of_retirement","date_of_joining"])
		
		### fetch employee based on experience and no of year of retirement
		experienced_and_non_retired_employees = []
		if len(all_active_employee_list)>0:
			for employee in all_active_employee_list:

				### if Qualification , Yeasr Of Experience and Year Of Retirement all are applicable

				if len(self.qualification)>0:
					employee_qualification = frappe.db.get_value("Employee Education",{"parent":employee.name},"custom_education_level")
					if employee_qualification and employee_qualification in [ele.qualification for ele in self.qualification]:
						# experienced_and_non_retired_employees.append(employee)
						if self.no_of_years_for_retirement>0:
							employee_years_of_retirement = month_diff(employee.date_of_retirement, today())/12
							if employee_years_of_retirement > self.no_of_years_for_retirement:
								if self.no_of_years_of_experience>0:
									employee_years_of_experience = self.get_no_of_year_of_experience(employee.name)
									if employee_years_of_experience:
										if employee_years_of_experience >= self.no_of_years_of_experience:
											if employee not in experienced_and_non_retired_employees:
												experienced_and_non_retired_employees.append(employee.name)
								else:
									if employee not in experienced_and_non_retired_employees:
										experienced_and_non_retired_employees.append(employee.name)
						elif self.no_of_years_of_experience>0:
							employee_years_of_experience = self.get_no_of_year_of_experience(employee.name)
							if employee_years_of_experience:
								if employee_years_of_experience >= self.no_of_years_of_experience:
									if employee not in experienced_and_non_retired_employees:
										experienced_and_non_retired_employees.append(employee.name)
						
						else :
							if employee not in experienced_and_non_retired_employees:
								experienced_and_non_retired_employees.append(employee.name)

				### If Only Yeasr Of Experience and Year Of Retirement all are applicable

				elif self.no_of_years_for_retirement>0:
					employee_years_of_retirement = month_diff(employee.date_of_retirement, today())/12
					if employee_years_of_retirement > self.no_of_years_for_retirement:
						if self.no_of_years_of_experience>0:
							employee_years_of_experience = self.get_no_of_year_of_experience(employee.name)
							if employee_years_of_experience:
								if employee_years_of_experience >= self.no_of_years_of_experience:
									if employee not in experienced_and_non_retired_employees:
										experienced_and_non_retired_employees.append(employee.name)
						else:
							if employee not in experienced_and_non_retired_employees:
								experienced_and_non_retired_employees.append(employee.name)
				
				### If Yeasr Of Experience is applicable

				elif self.no_of_years_of_experience>0:
					print("*"*10,)
					employee_years_of_experience = self.get_no_of_year_of_experience(employee.name)
					if employee_years_of_experience:
						if employee_years_of_experience >= self.no_of_years_of_experience:
							if employee not in experienced_and_non_retired_employees:
								experienced_and_non_retired_employees.append(employee.name)
				
				### No any filters 
				
				else :
					if employee not in experienced_and_non_retired_employees:
						experienced_and_non_retired_employees.append(employee.name)

		current_year = getdate(today()).year
		previous_year = getdate(add_to_date(today(), years=-1)).year
		final_employee_list = []
		print(self.previous_year_evaluation,"--------------------previous_year_evaluation")

		### fetch employee based on evaluation classification

		for emp in experienced_and_non_retired_employees:
			previous_evaluation = False
			current_evaluation = False
			employee_eveluation_list = frappe.db.get_all("Employee Evaluation ST",
											filters={"evaluation_type":self.evaluation_type,"employee_no":emp,"docstatus":1},
											fields=["name","evaluation_classification","evaluation_from","evaluation_to","employee_no","employee_name"])
			emp_details = {}
			if len(employee_eveluation_list)>0:
				for evaluation in employee_eveluation_list:
					if (evaluation.evaluation_from).year == previous_year and (evaluation.evaluation_to).year == previous_year:
						
						if len(self.previous_year_evaluation)>0:
							if evaluation.evaluation_classification in [ele.evaluation_classification for ele in self.previous_year_evaluation]:
								previous_evaluation = True
								emp_details["previous_year_evaluation"] = evaluation.evaluation_classification
							
					elif (evaluation.evaluation_from).year == current_year and (evaluation.evaluation_to).year == current_year:
						if len(self.current_year_evaluation)>0:
							if evaluation.evaluation_classification in [ele.evaluation_classification for ele in self.current_year_evaluation]:
								current_evaluation = True
								emp_details["current_year_evaluation"] = evaluation.evaluation_classification
			# if previous_evaluation == True and current_evaluation == True:
			emp_details["employee_no"]=emp
			final_employee_list.append(emp_details)
			# print(final_employee_list,"======")
		if len(final_employee_list)>0:
			for emp in final_employee_list:
				check_eployee_high_potential_record = frappe.db.get_all("High Performance Employee Details ST",
															filters={"employee_no":emp.get("employee_no"),"docstatus":1},
															fields=["name","employee_no","employee_psychometric_test_score","technical_evaluation"],order_by="modified desc")
				if len(check_eployee_high_potential_record)>0:
					emp["employee_psychometric_test_score"] = check_eployee_high_potential_record[0].employee_psychometric_test_score
					emp["technical_evaluation"] = check_eployee_high_potential_record[0].technical_evaluation
				else:
					emp["employee_psychometric_test_score"] = 0.0
					emp["technical_evaluation"] = 0.0
		return final_employee_list
	
	def get_no_of_year_of_experience(self, employee):
		employee_years_of_experience_str = frappe.db.get_value("Employee",employee,"custom_total_years_of_experience")
		if employee_years_of_experience_str :
			# print(employee_years_of_experience_str,"==++==",type(employee_years_of_experience_str),employee_years_of_experience_str[:2],cint(employee_years_of_experience_str[:2]))
			employee_years_of_experience_int = cint(employee_years_of_experience_str.split(' ')[0])
			return employee_years_of_experience_int