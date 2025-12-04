# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, add_to_date, get_datetime, get_date_str, cstr, get_first_day, get_last_day, getdate, time_diff_in_hours, get_link_to_form
from stats.hr_utils import check_if_holiday_between_applied_dates
from frappe.model.mapper import get_mapped_doc

class ScholarshipRequestST(Document):
	def validate(self):
		self.validate_duplicate_entry_based_on_employee_scholarship_and_specialisation_type()
		self.validate_terms_and_conditions_read()
		# self.validate_maximum_applications()
	
	def validate_terms_and_conditions_read(self):
		if self.terms_and_conditions:
			if self.i_agree_to_the_terms_and_conditions==0:
				frappe.throw(_("Please Read Terms & Conditions and check the checkbox below to conditions if agree with conditions"))

	def validate_duplicate_entry_based_on_employee_scholarship_and_specialisation_type(self):
		exists_scholarship = frappe.db.exists("Scholarship Request ST", {"employee_no": self.employee_no,"scholarship_no": self.scholarship_no,"specialisation_type": self.specialisation_type})
		print(exists_scholarship,self.employee_no,self.scholarship_no,self.specialisation_type,self.name,"--------------------")
		if exists_scholarship != None and exists_scholarship != self.name:
			frappe.throw(_("You cannot create Scholarship Request for same employee, scholarship no and specification type."))

	def validate_maximum_applications(self):
		if self.scholarship_no and self.specialisation_type:
			scholarship = frappe.db.get_all("Scholarship ST",filters={"scholarship_no":self.scholarship_no},fields=["name"])
			if len(scholarship)>0:
				scholarship_doc = frappe.get_doc("Scholarship ST",scholarship[0].name)
				for row in scholarship_doc.scholarship_details:
					if row.specialisation_type == self.specialisation_type:
						maximum_applicants = row.max_no_of_applicants
				scholarship_requests_list = frappe.db.get_all("Scholarship Request ST",
												  filters={"scholarship_no":self.scholarship_no,"specialisation_type":self.specialisation_type},
												  fields=["name"])
				print(len(scholarship_requests_list),"len(scholarship_requests_list)",maximum_applicants,"maximum_applicants")
				if len(scholarship_requests_list) and len(scholarship_requests_list) > maximum_applicants:
					frappe.throw(_("You cannot apply for scholarship because maximum limit is {0}").format(maximum_applicants))

	@frappe.whitelist()
	def fetch_scholarship_details_based_on_specialisation_type(self):
		if self.specialisation_type:
			scholarship_doc = frappe.get_doc("Scholarship ST",{"scholarship_no":self.scholarship_no})
			scholarship_details_list = frappe.db.get_all("Scholarship Details ST",
												filters={"parent":scholarship_doc.name,"specialisation_type":self.specialisation_type},
												fields=["qualification","english_required"])
			return scholarship_details_list, scholarship_doc.terms_and_conditions

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_open_scholarships(doctype, txt, searchfield, start, page_len, filters):
	open_scholarships = frappe.db.get_all("Scholarship ST",
									   filters={"docstatus":1,"status":"Open"},
									   fields=["scholarship_no"],as_list=1)
	return open_scholarships

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_specialisation_type_from_scholarship_no(doctype, txt, searchfield, start, page_len, filters):
	scholarship_no = filters.get("scholarship_no")
	scholarship_doc = frappe.get_doc("Scholarship ST",{"scholarship_no":scholarship_no})
	specialisation_type_list = frappe.db.get_all("Scholarship Details ST",
									   parent_doctype = "Scholarship ST",
									   filters={"parent":scholarship_doc.name},
									   fields=["specialisation_type"],as_list=1)
	return specialisation_type_list



@frappe.whitelist()
def create_extend_scholarship_from_request(source_name, target_doc=None):
	req_doc = frappe.get_doc("Scholarship Request ST",source_name)
	return_from_scholarship_exists = frappe.db.exists("Return From Scholarship ST",{"employee_no":req_doc.employee_no,"docstatus":1,"scholarship_no":req_doc.scholarship_no,"scholarship_request_reference":req_doc.name})
	if return_from_scholarship_exists == None:
		doc = get_mapped_doc(
			"Scholarship Request ST",
			source_name,
			{
				"Scholarship Request ST": {
					"doctype": "Scholarship Extend ST",
				}
			},
			target_doc
		)
	else:
		frappe.throw(_("You cannot create Scholarship Extend because you already submitted Return from scholarship {0}".format(get_link_to_form("Return From Scholarship ST",return_from_scholarship_exists))))
	return doc

@frappe.whitelist()
def create_return_from_scholarship(source_name, target_doc=None):
	req_doc = frappe.get_doc("Scholarship Request ST",source_name)
	return_from_scholarship_exists = frappe.db.exists("Return From Scholarship ST",{"employee_no":req_doc.employee_no,"docstatus":1,"scholarship_no":req_doc.scholarship_no,"scholarship_request_reference":req_doc.name})
	if return_from_scholarship_exists == None:
		doc = get_mapped_doc(
			"Scholarship Request ST",
			source_name,
			{
				"Scholarship Request ST": {
					"doctype": "Return From Scholarship ST",
				}
			},
			target_doc
		)
	else:
		frappe.throw(_("You cannot create Return From Scholarship again. You already create one {0}".format(get_link_to_form("Return From Scholarship ST",return_from_scholarship_exists))))
	return doc