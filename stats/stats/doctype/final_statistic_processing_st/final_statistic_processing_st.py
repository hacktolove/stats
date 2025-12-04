# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr, get_link_to_form, getdate
from frappe import _
from stats.budget import get_budget_account_details_without_cost_center

class FinalStatisticProcessingST(Document):
	def validate(self):
		self.calculate_total_cost_department_vise()
		self.get_available_budget()

	def on_submit(self):
		self.set_approval_status_in_statistic_request()

	def calculate_total_cost_department_vise(self):
		total_request_cost = 0
		self.total_request_cost=0
		#  set child table's total cost value
		for idx in range(self.no_of_department or 0):
			child_table_name="sub_department_"+cstr(idx+1)
			child_talbe_total_cost_name="total_cost_"+cstr(idx+1)
			total_cost_value=0
			for dep in self.get(child_table_name):
				total_cost_value = total_cost_value + (dep.final_cost or 0)
			
			total_request_cost = total_request_cost + total_cost_value
			print('total_request_cost',total_request_cost)
			self.set(child_talbe_total_cost_name,total_cost_value)
		
		# set parent level total request cost
		self.total_request_cost=total_request_cost
		for idx in range(self.no_of_department or 0):
			percentage_value=0
			child_table_percentage_name="percentage_"+cstr(idx+1)
			child_talbe_total_cost_name="total_cost_"+cstr(idx+1)
			percentage_value=((self.get(child_talbe_total_cost_name)  or 0)* 100) / total_request_cost
			self.set(child_table_percentage_name,percentage_value)		

	def get_available_budget(self):
		default_budget_account_for_statistic_expense = frappe.db.get_single_value("Stats Settings ST","default_budget_account")
		fiscal_year = getdate(self.to_date).year
		account_details = get_budget_account_details_without_cost_center(default_budget_account_for_statistic_expense,fiscal_year)

		if account_details:
			self.available_budget = account_details.available
	
	def set_approval_status_in_statistic_request(self):
		for idx in range(self.no_of_department or 0):
			child_table_name="sub_department_"+cstr(idx+1)
			for dep in self.get(child_table_name):
				doc = frappe.get_doc("Statistic Request ST", dep.statistic_request_reference)
				if dep.action == "Approve":
					doc.approval_status = "Final Approval"
					doc.add_comment("Comment",text="This Doc Updated Because Of Final Statistic Processing {0} doc.".format(get_link_to_form("Final Statistic Processing ST",self.name)))
					doc.save(ignore_permissions=True)
				elif dep.action == "Reject":
					doc.approval_status = "Rejected"
					doc.add_comment("Comment",text="This Doc Updated Because Of Final Statistic Processing {0} doc.".format(get_link_to_form("Final Statistic Processing ST",self.name)))
					doc.save(ignore_permissions=True)
				else:
					continue				

	@frappe.whitelist()
	def fetch_department_vise_statistic_request(self):
		# empty child table values
		total_no_of_child_table=10
		for idx in range(total_no_of_child_table):
			child_table_name="sub_department_"+cstr(idx+1)
			child_table_sub_department_name="sub_department_name"+cstr(idx+1)
			child_talbe_total_cost_name="total_cost_"+cstr(idx+1)
			child_table_percentage_name="percentage_"+cstr(idx+1)
			self.set(child_table_name,[])
			self.set(child_table_sub_department_name,None)
			self.set(child_talbe_total_cost_name,None)
			self.set(child_table_percentage_name,None)


		statistic_request_list = frappe.db.get_all("Statistic Request ST", filters={"approval_status":"Initial Approval", "docstatus":1,"creation_date":["between",[self.from_date,self.to_date]]}, fields=["name", "sub_department"],
											 order_by='sub_department')
		
		if len(statistic_request_list)<1:
			frappe.msgprint(_("No matching records found"))
			return
		unique_sub_departments = []
		for dep in statistic_request_list:
			if dep.sub_department not in unique_sub_departments:
				unique_sub_departments.append(dep.sub_department)

		self.no_of_department = len(unique_sub_departments)

		#  set sub department name
		for idx,unique in enumerate(unique_sub_departments):
			child_table_sub_department_name="sub_department_name"+cstr(idx+1)
			for dep in statistic_request_list:
				if unique == dep.sub_department:			
					self.set(child_table_sub_department_name,dep.sub_department)
					break

		for idx,unique in enumerate(unique_sub_departments):
			for dep in statistic_request_list:
				if unique == dep.sub_department:
					child_table_name="sub_department_"+cstr(idx+1)
					dep1 = self.append(child_table_name, {})
					dep1.statistic_request_reference = dep.name

		self.save(ignore_permissions=True)