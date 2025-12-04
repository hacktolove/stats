# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form,today,flt
from stats.salary import get_latest_basic_salary_of_employee, get_latest_salary_structure_assignment


class EmployeeReallocationSheetST(Document):
	def validate(self):
		self.get_employee_basic_and_transport_salary()
	
	def on_submit(self):
		self.change_employee_reallocation_status()
		self.create_payment_request_on_submit_of_reallocation_sheet()

	def change_employee_reallocation_status(self):
		if len(self.employee_reallocation_request_details):
			for row in self.employee_reallocation_request_details:
				employee_reallocation_doc = frappe.get_doc("Employee Reallocation ST",row.reallocation_reference)
				employee_reallocation_doc.process_status = "Processed"
				employee_reallocation_doc.save(ignore_permissions = True)
				frappe.msgprint(_("Status of {0} is changed to Processed").format(get_link_to_form("Employee Reallocation ST",employee_reallocation_doc.name)),alert=True)
	
	def create_payment_request_on_submit_of_reallocation_sheet(self):
		company = erpnext.get_default_company()
		company_default_reallocation_budget_expense_account = frappe.db.get_value("Company",company,"custom_reallocation_budget_expense_account")
		pr_doc = frappe.new_doc("Payment Request ST")
		pr_doc.date = today()
		pr_doc.reference_name = "Employee Reallocation Sheet ST"
		pr_doc.reference_no = self.name
		pr_doc.budget_account = company_default_reallocation_budget_expense_account
		pr_doc.party_type = "Employee"
		pr_doc.type = "Classified"
		
		if len(self.employee_reallocation_request_details)>0:
			for row in self.employee_reallocation_request_details:
				pr_row = pr_doc.append("employees",{})
				pr_row.employee_no = row.employee_no
				pr_row.amount = row.due_amount

		pr_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Request {0} is created").format(get_link_to_form("Payment Request ST", pr_doc.name)),alert=1)
	
	@frappe.whitelist()
	def fetch_employee_reallocation_request(self):
			
		filters={"docstatus":1,"process_status": "Pending","add_reallocation_amount":"Yes"}

		if self.from_date and self.to_date:
			filters["transaction_date"]=["between", [self.from_date, self.to_date]]
		if self.main_department:
			filters["main_department"]=self.main_department
		if self.sub_department:
			filters["sub_department"]=self.sub_department
		if self.branch:
			filters["branch"]=self.branch

		employee_reallocation_request_list = frappe.db.get_all('Employee Reallocation ST', filters=filters,fields=["name"],debug=1)

		if len(employee_reallocation_request_list) < 1:
			frappe.msgprint(_("No data found"))

		return employee_reallocation_request_list

	def get_employee_basic_and_transport_salary(self):
		if len(self.employee_reallocation_request_details) > 0:
			for row in self.employee_reallocation_request_details:
				basic_salary = 0
				transportation_amount = 0
				latest_salary_structure_assignment = get_latest_salary_structure_assignment(row.employee_no,row.date)
				print(latest_salary_structure_assignment,"latest_salary_structure_assignment ==============")
				if latest_salary_structure_assignment:
					latest_salary_structure = frappe.db.get_value("Salary Structure Assignment",latest_salary_structure_assignment,"salary_structure")
					if latest_salary_structure:
						salary_structure_doc = frappe.get_doc("Salary Structure",latest_salary_structure)
						transportation_component = frappe.db.get_single_value("Stats Settings ST","overtime_transportation_earning_component")
						basic_salary_component = frappe.db.get_value("Employee Grade",row.grade,"custom_basic_salary_component")
						print(latest_salary_structure, transportation_component, basic_salary_component,"latest_salary_structure, transportation_component, basic_salary_component =============="	)
						if len(salary_structure_doc.earnings)>0:
							for d in salary_structure_doc.earnings:
								if transportation_component:
									if d.salary_component == transportation_component:
										transportation_amount = d.amount
								if basic_salary_component:
									if d.salary_component == basic_salary_component:
										basic_salary = d.amount
							row.basic_salary = basic_salary
							row.transportation_amount = transportation_amount