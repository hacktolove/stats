# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import today, get_link_to_form
from frappe.model.document import Document


class EducationAllowanceSheetST(Document):
	def validate(self):
		self.calculate_approved_amount()

	def calculate_approved_amount(self):
			total_approved_amount = 0
			if len(self.education_allowance_sheet_details)>0:
				for row in self.education_allowance_sheet_details:
					total_approved_amount = total_approved_amount + row.approved_amount
			
			self.total_approved_amount = total_approved_amount

	def on_submit(self):
	# def validate(self):
		self.create_payment_request_on_submit_of_sheet()
		self.change_status_of_allowance_request()

	def create_payment_request_on_submit_of_sheet(self):
		company = erpnext.get_default_company()
		company_education_allowance_expense_account = frappe.db.get_value("Company",company,"custom_education_allowance_expense_account")
		pr_doc = frappe.new_doc("Payment Request ST")
		pr_doc.date = today()
		pr_doc.reference_name = self.doctype
		pr_doc.reference_no = self.name
		pr_doc.budget_account = company_education_allowance_expense_account
		pr_doc.party_type = "Employee"
		pr_doc.type = "Classified"

		employee_details = frappe.db.sql("""
								SELECT
									ead.employee_no ,
									sum(ead.approved_amount) as approved_amount
								FROM
									`tabEducation Allowance Sheet Details ST` as ead
								INNER JOIN `tabEducation Allowance Sheet ST` as eas on
									ead.parent = eas.name
								WHERE eas.name = %s
								GROUP BY
									ead.employee_no
						""",self.name,as_dict=True,debug=True)
		print(employee_details,"---------------")

		if len(employee_details)>0:
			for row in employee_details:
				pr_row = pr_doc.append("employees",{})
				pr_row.employee_no = row.employee_no
				pr_row.amount = row.approved_amount
		pr_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Request {0} is created").format(get_link_to_form("Payment Request ST", pr_doc.name)),alert=1)
	
	def change_status_of_allowance_request(self):
		if len(self.education_allowance_sheet_details)>0:
			for row in self.education_allowance_sheet_details:
				allowance_request_doc = frappe.get_doc("Education Allowance Request ST",row.education_allowance_request_reference)
				allowance_request_doc.payment_status = "Paid"
				allowance_request_doc.add_comment("Comment",text="Payment Status changed to <b>Paid</b> due to {0}".format(get_link_to_form("Education Allowance Sheet ST",self.name)))
				allowance_request_doc.save(ignore_permissions=True)
			frappe.msgprint(_("Payment status is changed of {0}").format(get_link_to_form("Education Allowance Request ST", row.education_allowance_request_reference)),alert=1)

	@frappe.whitelist()
	def fetch_education_allowance_requests(self):

		filters={"docstatus":1,"payment_status":"Pending","creation_date":["between", [self.request_date_from, self.request_date_to]]}
		if self.season:
			filters["season_type"]=self.season

		allowance_request_list = frappe.db.get_all("Education Allowance Request ST",
											 filters=filters,
											 fields=["name","employee_no","approved_amount"])
		return allowance_request_list