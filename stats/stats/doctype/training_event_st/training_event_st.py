# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import get_link_to_form, getdate, date_diff, today
from frappe.model.document import Document
from erpnext.manufacturing.doctype.workstation.workstation import get_default_holiday_list


class TrainingEventST(Document):
	def validate(self):
		self.validate_start_date_and_end_date()
		self.calculate_no_of_days()

	def validate_start_date_and_end_date(self):
		if self.training_start_date:
			if getdate(self.training_start_date) < getdate(today()):
				frappe.msgprint(_("Training Start Date is less than today date"))
		if self.training_start_date and self.training_end_date:
			if getdate(self.training_end_date) < getdate(self.training_start_date):
				frappe.throw(_("End date can not be less than Start date"))

	def calculate_no_of_days(self):

		if self.training_start_date and self.training_end_date:
			no_of_day = date_diff(self.training_end_date, self.training_start_date) + 1

			if self.ignore_holidays_in_no_of_days == 1:
				fiscal_year_doc = frappe.get_doc("Fiscal Year",getdate(self.training_start_date).year)
				exist_holiday_list = frappe.db.get_all("Holiday List",
											filters={"to_date":fiscal_year_doc.year_end_date,"from_date":fiscal_year_doc.year_start_date},
											fields=["name"],limit=1)
				if len(exist_holiday_list)<1:
					frappe.throw(_("Holiday list for year <b>{0}</b> does not exists. Hence we cannot get holiday to ignore").format(getdate(self.training_start_date).year))

				holiday_count = 0
				if exist_holiday_list:
					holidays = frappe.db.get_all("Holiday",
										parent_doctype="Holiday List",
										filters={"parent":exist_holiday_list[0].name,"holiday_date":["between",[self.training_start_date,self.training_end_date]]},
										fields=["name"])
					if len(holidays)>0:
						holiday_count = len(holidays)
				
				self.no_of_days = no_of_day - holiday_count
			else :
				self.no_of_days = no_of_day
		

	def on_submit(self):
		if self.training_status == "Closed":
			self.create_evaluation_for_all_employees()
			# if len(self.training_event_employee_details)>0:
			# 	for row in self.training_event_employee_details:
			# 		frappe.db.set_value("Training Request ST",row.training_request_reference,"status","Finished")
			# 		frappe.msgprint(_("Status of {0} is changed to {1}").format(get_link_to_form("Training Request ST", row.training_request_reference),"Finished"),alert=1)
			# 		create_training_evaluation(self.name,row.employee_no)
			# 		frappe.db.set_value("Training Event ST",self.name,"training_status","Finished")
	
	def on_update_after_submit(self):
		self.create_evaluation_for_all_employees()
		# if self.training_status == "Closed":
		# 	if len(self.training_event_employee_details)>0:
		# 		for row in self.training_event_employee_details:
		# 			frappe.db.set_value("Training Request ST",row.training_request_reference,"status","Finished")
		# 			frappe.msgprint(_("Status of {0} is changed to {1}").format(get_link_to_form("Training Request ST", row.training_request_reference),"Finished"),alert=1)
		# 			create_training_evaluation(self.name,row.employee_no)
		# 			frappe.db.set_value("Training Event ST",self.name,"training_status","Finished")

	def create_evaluation_for_all_employees(self):
		if self.training_status == "Closed":
			if len(self.training_event_employee_details)>0:
				for row in self.training_event_employee_details:
					frappe.db.set_value("Training Request ST",row.training_request_reference,"status","Finished")
					frappe.msgprint(_("Status of {0} is changed to {1}").format(get_link_to_form("Training Request ST", row.training_request_reference),"Finished"),alert=1)
					create_training_evaluation(self.name,row.employee_no)
					frappe.db.set_value("Training Event ST",self.name,"training_status","Finished")
	
	# def on_cancel(self):
	# 	print("on_cancel")
	# 	if len(self.training_event_employee_details)>0:
	# 		for row in self.training_event_employee_details:
	# 			training_request_doc = frappe.get_doc("Training Request ST",row.training_request_reference)
	# 			training_request_doc.cancel()
	# 			frappe.msgprint(_("Training Request {0} is cancelled").format(get_link_to_form("Training Request ST", row.training_request_reference)),alert=1)
	
	def on_trash(self):
		print("on_trash")
		if len(self.training_event_employee_details)>0:
			for row in self.training_event_employee_details:
				if row.training_request_reference:
					training_request_doc = frappe.get_doc("Training Request ST",row.training_request_reference)
					exists_needs_analysis = frappe.db.get_all("Training Needs Analysis Employee Details ST",
												filters = {"training_request_reference":training_request_doc.name},
												fields = ["parent"])
					if len(exists_needs_analysis)>0:
						needs_analysis_doc = frappe.get_doc("Training Needs Analysis ST",exists_needs_analysis[0].parent)
						needs_analysis_doc.delete()
						frappe.msgprint(_("Training Needs Analysis {0} is deleted").format(exists_needs_analysis[0].parent),alert=1)
					training_request_doc.delete()

					training_eveluation = frappe.db.get_all("Training Evaluation ST",
												filters = {"training_event":self.name,"employee_no":row.employee_no},
												fields = ["name"])
					if len(training_eveluation)>0:
						training_eveluation_doc = frappe.get_doc("Training Evaluation ST",training_eveluation[0].name)
						training_eveluation_doc.delete()
					
					frappe.msgprint(_("Training Request {0} is deleted").format(row.training_request_reference),alert=1)
		
	@frappe.whitelist()
	def fetch_training_request(self):
		approved_training_request_list = frappe.db.get_all("Training Request ST",
													 filters = {"training_event":self.name,"docstatus":1,"status":"Accepted"},
													 fields=["name","employee_no"])
		return approved_training_request_list
	
	@frappe.whitelist()
	def check_holiday_between_start_end_date(self):
		print("---------------------")
		default_holiday_list = get_default_holiday_list()
		print(default_holiday_list,"default_holiday_list")
		if default_holiday_list:
			holidays = frappe.db.get_all("Holiday",
								parent_doctype="Holiday List",
								filters={"parent":default_holiday_list,"holiday_date":["between",[self.training_start_date,self.training_end_date]]},
								fields=["name"])
			if len(holidays)>0:
				holiday_count = len(holidays)
				return holiday_count

def create_training_evaluation(training_event,employee):
		training_evaluation_doc = frappe.new_doc("Training Evaluation ST")
		training_evaluation_doc.employee_no = employee
		training_evaluation_doc.training_event = training_event
		training_evaluation_doc.run_method("set_missing_values")
		training_evaluation_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Training Evaluation is created {0}").format(get_link_to_form("Training Evaluation ST",training_evaluation_doc.name)),alert=True)
		return training_evaluation_doc.name