# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import today, get_link_to_form
from frappe.model.document import Document


class EndOfServiceSheetST(Document):

	def on_submit(self):
		self.create_payment_request_on_submit_of_sheet()
	
	@frappe.whitelist()
	def get_employee_details_for_end_of_service(self):

		eos_list = []
		resignation_list = frappe.db.get_all("End of Service Calculation ST", filters={"creation_date":["Between", [self.from_date, self.to_date]],"docstatus":1},
							   fields=["name", "employee", "total_monthly_salary", "end_of_service_due_amount"])
		
		eos_details = {}
		for res in resignation_list:
			eos_details["employee_no"] = res.employee
			eos_details["reference"] = res.name
			eos_details["total_salary"] = res.total_monthly_salary
			eos_details["due_amount"] = res.end_of_service_due_amount
			eos_details["eos_type"] = "Resignation"
			eos_list.append(eos_details)
			eos_details = {}
		
		retriement_list = frappe.db.get_all("Retirement Request ST", filters={"creation_date": ["Between", [self.from_date, self.to_date]], "docstatus":1},
									  fields=["name", "employee_no", "total_monthly_salary", "new_retirement_due_amount"])
		
		for ret in retriement_list:
			eos_details["employee_no"] = ret.employee_no
			eos_details["reference"] = ret.name
			eos_details["total_salary"] = ret.total_monthly_salary
			eos_details["due_amount"] = ret.new_retirement_due_amount
			eos_details["eos_type"] = "Retirement"

			print(ret.new_retirement_due_amount, "$$$$$$$ret.new_retirement_due_amount")
			eos_list.append(eos_details)
			eos_details = {}

		print(eos_list, "===breforeee eos_list")

		eos_sheet_list = frappe.db.get_all("End Of Service Sheet ST", filters={"docstatus":1, "name":["!=", self.name]}, fields=["name"])

		for sheet in eos_sheet_list:
			eos_sheet = frappe.get_doc("End Of Service Sheet ST", sheet.name)
			for emp in eos_sheet.employee_details:
				for a in eos_list:
					if emp.reference == a.get('reference'):
						eos_list.remove(a)
				else:
					continue

		print(eos_list, "===afterrrr eos_list")
		
		return eos_list

	def create_payment_request_on_submit_of_sheet(self):
		company = erpnext.get_default_company()
		company_default_end_of_service_allocated_account = frappe.db.get_value("Company",company,"custom_default_end_of_service_allocated_account")
		pr_doc = frappe.new_doc("Payment Request ST")
		pr_doc.date = today()
		pr_doc.reference_name = self.doctype
		pr_doc.reference_no = self.name
		pr_doc.budget_account = company_default_end_of_service_allocated_account
		pr_doc.party_type = "Employee"
		pr_doc.type = "Classified"
		
		if len(self.employee_details)>0:
			for row in self.employee_details:
				pr_row = pr_doc.append("employees",{})
				pr_row.employee_no = row.employee_no
				pr_row.amount = row.due_amount

		pr_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Request {0} is created").format(get_link_to_form("Payment Request ST", pr_doc.name)),alert=1)