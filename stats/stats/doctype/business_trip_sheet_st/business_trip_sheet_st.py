# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form, flt
from stats.api import fetch_employee_per_diem_amount
from frappe.utils import today
from stats.salary import get_latest_salary_structure_assignment


class BusinessTripSheetST(Document):
	def validate(self):
		self.set_no_of_days_in_child_table()
		self.set_location_based_on_classification_type()
		self.calculate_approved_amount()
		# self.set_ticket_amount_and_total_amount_per_employee()
		self.validate_start_date_and_end_date()
		self.calculate_total_amount()

	def calculate_approved_amount(self):
		if len(self.employee_detail)>0:
			for row in self.employee_detail:
				transportation_amount = 0
				approved_amount = 0
				transportation_due_amount = 0
				
				employee_no,trip_type = frappe.db.get_value("Business Trip Request ST",row.business_trip_reference,["employee_no","trip_classification"])
				approved_amount, per_diem_amount = fetch_employee_per_diem_amount(employee_no,row.approved_days,trip_type)
				print(approved_amount,"approved_amount")
				
				employee_contract_type = frappe.db.get_value("Employee",row.employee_no,"custom_contract_type")
				if employee_contract_type:
					contract_actual_type = frappe.db.get_value("Contract Type ST",employee_contract_type,"contract")
					print(contract_actual_type, '---contract_actual_type')
					if contract_actual_type and contract_actual_type == "Civil":
						transportation_component = frappe.db.get_single_value("Stats Settings ST","overtime_transportation_earning_component")	
						latest_salary_structure_assignment = get_latest_salary_structure_assignment(row.employee_no,today())
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
						# transportation_amount = frappe.db.get_value("Business Trip Request ST",row.business_trip_reference,"transportation_amount")
						transportation_due_amount = transportation_amount_per_day * (row.approved_days or 0)
						row.transportation_amount = transportation_amount
						row.transportation_amount_per_day = transportation_amount_per_day
						row.transportation_due_amount = transportation_due_amount

				row.per_diem_amount = per_diem_amount
				row.approved_amount = approved_amount + transportation_due_amount
	
	# def set_ticket_amount_and_total_amount_per_employee(self):
	# 	if len(self.employee_detail)>0:
	# 		for row in self.employee_detail:
	# 			ticket_request_name = frappe.db.get_all("Ticket Request ST",filters={"business_trip_reference":row.business_trip_reference},fields=["name"])
	# 			if len(ticket_request_name)>0:
	# 				ticket_value = frappe.db.get_value("Ticket Request ST",ticket_request_name[0].name,"ticket_value")
	# 				row.ticket_amount = ticket_value
	# 			row.total_amount = (row.ticket_amount or 0) + (row.approved_amount or 0)

	def validate_start_date_and_end_date(self):
		if self.from_date and self.to_date:
			if self.to_date < self.from_date:
				frappe.throw(_("End date can not be less than Start date"))
			
	def set_no_of_days_in_child_table(self):
		if len(self.employee_detail)>0:
			for row in self.employee_detail:
				if row.employee_task_completion_reference:
					business_trip_reuest_reference = frappe.db.get_value("Employee Task Completion ST",row.employee_task_completion_reference,"business_trip_reference")
					if business_trip_reuest_reference:
						total_no_of_days = frappe.db.get_value("Business Trip Request ST",business_trip_reuest_reference,"total_no_of_days")
						if total_no_of_days:
							row.approved_days = total_no_of_days

	def set_location_based_on_classification_type(self):
		if len(self.employee_detail)>0:
			for row in self.employee_detail:
				location = ""
				if row.business_trip_reference:
					trip_classification = frappe.db.get_value("Business Trip Request ST",row.business_trip_reference,"trip_classification")
					print(trip_classification, "================trip_classification====")
					if _(trip_classification) == _("Internal"):
						location = frappe.db.get_value("Business Trip Request ST",row.business_trip_reference,"saudi_city")
					if _(trip_classification) == _("External"):
						location = frappe.db.get_value("Business Trip Request ST",row.business_trip_reference,"country")
					row.location = location
	
	def calculate_total_amount(self):
		total_amount = 0
		if len(self.employee_detail)>0:
			for row in self.employee_detail:
				total_amount = total_amount + row.approved_amount
		self.total_amount = total_amount

	def on_submit(self):
		if len(self.employee_detail)>0:
			for row in self.employee_detail:
				frappe.db.set_value("Employee Task Completion ST",row.employee_task_completion_reference,"process_status","Processed")
				frappe.msgprint(_("Process status of {0} is changed to {1}").format(get_link_to_form("Employee Task Completion ST", row.employee_task_completion_reference),"Processed"),alert=1)
				ticket_request_name = frappe.db.get_all("Ticket Request ST",filters={"business_trip_reference":row.business_trip_reference},fields=["name"])
				if len(ticket_request_name)>0:
					frappe.db.set_value("Ticket Request ST",ticket_request_name[0].name,"process_status","Processed")
					frappe.msgprint(_("Process status of {0} is changed to {1}").format(get_link_to_form("Ticket Request ST", ticket_request_name[0].name),"Processed"),alert=1)
				
			self.create_payment_request_on_submit_of_bts()

	def create_payment_request_on_submit_of_bts(self):
		company = erpnext.get_default_company()
		company_default_business_trip_budget_expense_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_expense_account")
		pr_doc = frappe.new_doc("Payment Request ST")
		pr_doc.date = today()
		pr_doc.reference_name = "Business Trip Sheet ST"
		pr_doc.reference_no = self.name
		pr_doc.budget_account = company_default_business_trip_budget_expense_account
		pr_doc.party_type = "Employee"
		pr_doc.type = "Classified"
		
		if len(self.employee_detail)>0:
			for row in self.employee_detail:
				pr_row = pr_doc.append("employees",{})
				pr_row.employee_no = row.employee_no
				pr_row.amount = row.approved_amount

		pr_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Request {0} is created").format(get_link_to_form("Payment Request ST", pr_doc.name)),alert=1)

	@frappe.whitelist()
	def get_business_trip(self):
		if not self.from_date:
			frappe.throw(_("From date is required"))
		if not self.to_date:
			frappe.throw(_("To date is required"))

		filters={"docstatus":1,"process_status": "Pending","task_creation_date":["between", [self.from_date, self.to_date]]}
		# if self.main_department:
		# 	filters["main_department"]=self.main_department
		# if self.sub_department:
		# 	filters["sub_department"]=self.sub_department
		etc = frappe.db.get_all('Employee Task Completion ST', filters=filters,fields=["name"])
		print(etc, '--------etc')
		return etc