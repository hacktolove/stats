# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import month_diff, today, flt, getdate, add_to_date, get_link_to_form
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import today


class EducationAllowanceRequestST(Document):
	
	def validate(self):
		# self.set_season_type_based_on_date()
		self.validate_employee_not_in_test_period()
		self.calculate_and_validate_employee_kids_no()
		self.validate_terms_and_conditions_read()
		self.add_history()
		# self.calculate_and_validate_approved_amount()
		# self.validate_child_eligibility_based_on_requested_amount()
		self.validate_exceed_limit_of_amount()
		self.calculate_approved_amount()
		# self.calculate_unpaid_amount()
		self.validate_per_child_per_release()

		### comment because: new validation --> can apply for same season till per season amount limit fully consumed. --> check new function : validate_child_eligibility_based_on_requested_amount
		# self.validate_duplicate_record()
	
	def on_submit(self):
		self.deduct_allowance_amount_from_employee_profile_in_dependants_table()

	def validate_duplicate_record(self):
		exist_request = frappe.db.exists("Education Allowance Request ST", {"name":["!=",self.name],"employee_no":self.employee_no,"educational_year":self.educational_year,"season_type":self.season})
		if exist_request != None:
			frappe.throw(_("You cannot create request again for same Educational year and Season"))
	
	def add_history(self):
		history_list = self.get_employee_dependants_history()
		self.set("employee_education_allowance_history", [])
		if len(history_list)>0:
			for row in history_list:
				history = self.append("employee_education_allowance_history", {})
				history.child_name = row.child_name
				history.relation = row.relation
				history.date_of_birth = row.date_of_birth
				history.age = row.age
				history.requested_amount = row.requested_amount
				history.approved_amount = row.approved_amount
				history.ed_due_amount = row.ed_due_amount
				history.payment_attachment = row.payment_attachment
				history.season = row.season
				history.child_reference = row.child_reference
				history.id_number = row.id_number
				history.ed_balance_amount = row.ed_balance_amount
				history.season_type = row.season_type
				history.exceed_limit = row.exceed_limit
		
	@frappe.whitelist()
	def validate_per_child_per_release(self):
		if len(self.education_allowance_request_details)>0:
			for row in self.education_allowance_request_details:
				request_exists_in_same_release = frappe.db.sql("""
				SELECT
					ear.name,
					eard.child_name ,
					eard.child_reference
				FROM
					`tabEducation Allowance Request ST` ear
				INNER JOIN `tabEducation Allowance Request Details ST` eard ON
					ear.name = eard.parent
				WHERE
					ear.release_reference = '{0}'
					and ear.employee_no = '{1}'
					and eard.child_reference = '{2}'
					and ear.docstatus = 1
				""".format(self.release_reference, self.employee_no,row.child_reference),as_dict=True)
				if len(request_exists_in_same_release)>0:
					frappe.throw(_("You cannot request education allowance for {0} in same release again.".format(row.child_name)))

	def set_season_type_based_on_date(self):
		stats_settings_doc = frappe.get_doc("Stats Settings ST","Stats Settings ST")
		print(self.creation_date, "---self.creation_date---", type(self.creation_date))
		print(stats_settings_doc.first_season_apply_start_date, "---stats_settings_doc.first_season_apply_start_date---", type(stats_settings_doc.first_season_apply_start_date))
		creation_date = getdate(self.creation_date)
		if (creation_date.month == getdate(stats_settings_doc.first_season_apply_start_date).month) and (
			creation_date.day >= getdate(stats_settings_doc.first_season_apply_start_date).day or 
			creation_date.day <= getdate(stats_settings_doc.first_season_apply_end_date).day):
			self.season = "First Season"
		elif (creation_date.month == getdate(stats_settings_doc.second_season_apply_start_date).month) and (
			creation_date.day >= getdate(stats_settings_doc.second_season_apply_start_date).day or 
			creation_date.day <= getdate(stats_settings_doc.second_season_apply_end_date).day):
			self.season = "Second Season"
		elif (creation_date.month == getdate(stats_settings_doc.third_season_apply_start_date).month) and (
			creation_date.day >= getdate(stats_settings_doc.third_season_apply_start_date).day or 
			creation_date.day <= getdate(stats_settings_doc.third_season_apply_end_date).day):
			self.season = "Third Season"
		
		if self.season == None or self.season == "":
			frappe.throw(_("You cannot apply for education allowance on {0}.<br>It does not belongs to any season.".format(self.creation_date)))
		
	def validate_employee_not_in_test_period(self):
		employee_joining_date = frappe.db.get_value("Employee",self.employee_no,"date_of_joining")
		test_period = add_to_date(getdate(employee_joining_date), months=6)
		if test_period > getdate(self.creation_date): 
				frappe.throw(_("Employee is in test period<br>Hence cannot apply for Education Allowance"))
	
	def validate_terms_and_conditions_read(self):
		if self.terms_and_conditions:
			if self.i_agree_to_the_terms_and_conditions==0:
				frappe.throw(_("Please Read Terms & Conditions and check the checkbox below to conditions if agree with conditions"))
	
	def calculate_and_validate_employee_kids_no(self):
		maximum_kids_allowed_for_education_allowance = frappe.db.get_single_value("Stats Settings ST","maximum_kids_allowed_for_education_allowance")
		if maximum_kids_allowed_for_education_allowance == 0:
			frappe.throw(_("Please set Maximum Kids Allowed for Education Allowance in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))
		if len(self.education_allowance_request_details)>0:
			no_of_kids = len(self.education_allowance_request_details)
			if no_of_kids > maximum_kids_allowed_for_education_allowance:
				frappe.throw(_("You cannot add more than {0} kids for Education Allowance".format(maximum_kids_allowed_for_education_allowance)))
			self.no_of_kids = no_of_kids
		
		previous_requests = frappe.db.get_all("Education Allowance Request ST",
												  filters={"employee_no":self.employee_no,"educational_year":self.educational_year,"docstatus":1},
												  fields=["name"])
		applied_kids_list = []
		applied_kids_name = []
		if len(previous_requests)>0:
			for request in previous_requests:
				if request.name != self.name:
					kids_in_request = frappe.db.get_all("Education Allowance Request Details ST",
													filters={"parent":request.name},
													fields=["child_reference","child_name"])
					if len(kids_in_request)>0:
						for kid in kids_in_request:
							if kid.child_reference not in applied_kids_list:
								applied_kids_list.append(kid.child_reference)
								applied_kids_name.append(kid.child_name)
		applied_kids_name_str = ', '.join(applied_kids_name)
		if len(self.education_allowance_request_details)>0:
			for row in self.education_allowance_request_details:
				if row.child_reference not in applied_kids_list:
					if len(applied_kids_list) < maximum_kids_allowed_for_education_allowance:
					
						applied_kids_list.append(row.child_reference)
						applied_kids_name.append(row.child_name)
					else:
						frappe.throw(_("You cannot apply for more than {0} child<br>You already applied Education Allowance for <b>{1}</b>".format(maximum_kids_allowed_for_education_allowance,applied_kids_name_str)))

	def calculate_approved_amount(self):
		approved_amount = 0
		if len(self.education_allowance_request_details)>0:
			for row in self.education_allowance_request_details:
				if row.approved_amount and row.approved_amount > 0:
					approved_amount = approved_amount + row.approved_amount

		self.approved_amount = approved_amount
	
	@frappe.whitelist()
	def validate_child_eligibility_based_on_requested_amount(self):
		education_allowance_amount = frappe.db.get_value("Employee Grade",self.grade,"custom_education_allowance_amount")
		payment_percentage = frappe.db.get_value("Payment Season Details ST",{"payment_season":self.season},"payment_percentage")
		per_season_amount_limit = (flt(education_allowance_amount) * flt(payment_percentage)) / 100

		if len(self.education_allowance_request_details)>0:
			for row in self.education_allowance_request_details:
				consumed_amount = 0
				actual_allowed_amount = per_season_amount_limit
				other_allowance_request_for_same_season_and_year = frappe.db.sql("""
				SELECT
					edar.name request_name,
					edar.educational_year,
					edar.season,
					edar.employee_no,
					edard.child_name,
					edard.child_reference,
					edard.approved_amount,
					edard.requested_amount,
					edard.ed_due_amount
				FROM
					`tabEducation Allowance Request ST` edar
				INNER JOIN 
					`tabEducation Allowance Request Details ST` edard
				ON
					edar.name = edard.parent
				WHERE 
					edar.docstatus = 1 and edar.educational_year = '{0}' and edar.season = '{1}' and edar.employee_no = '{2}' and edard.child_reference = '{3}'
					""".format(self.educational_year,self.season,self.employee_no,row.child_reference), as_dict=1,debug=1)
				print(other_allowance_request_for_same_season_and_year,"---other_allowance_request_for_same_season_and_year---")
				if len(other_allowance_request_for_same_season_and_year)>0:
					for request in other_allowance_request_for_same_season_and_year:
						if request.request_name != self.name:
							actual_allowed_amount = actual_allowed_amount - flt(request.approved_amount)
							consumed_amount = consumed_amount + flt(request.approved_amount)
							if actual_allowed_amount < 0:
								actual_allowed_amount = 0
				print(actual_allowed_amount,"actual-----")
				if row.approved_amount and row.approved_amount > 0:
					if actual_allowed_amount == 0:
						frappe.throw(_("# Row {0}: You cannot apply for {1} in {2}.<br>Your allowance amount for this season is already consumed.<br>Allowance amount for {3} is {4}".format(row.idx,row.child_name,self.season,self.season,(flt(education_allowance_amount) * flt(payment_percentage)) / 100)))
					# else:
					# 	if row.approved_amount > actual_allowed_amount:
					# 		allow_to_exceed_limit = frappe.db.get_value("Payment Season Details ST",{"payment_season":self.season},"allow_to_exceed")
					# 		if allow_to_exceed_limit == _("No"):
					# 			frappe.throw(_("# Row {0}: Your requested amount cannot be greater than {1}<br>Your allowance amount per season per child is {2}".format(row.idx,flt(actual_allowed_amount,2),per_season_amount_limit)))
	
	def validate_exceed_limit_of_amount(self):
		print(self.grade,"<------- Grade")
		education_allowance_amount = frappe.db.get_value("Employee Grade",self.grade,"custom_education_allowance_amount")
		print(education_allowance_amount,"<------- education_allowance_amount from grade")
		print(self.season,"<------- season")
		payment_percentage = frappe.db.get_value("Payment Season Details ST",{"payment_season":self.season},"payment_percentage")
		print(payment_percentage,"<------- payment_percentage from stats settings")
		actual_allowed_amount = (flt(education_allowance_amount) * flt(payment_percentage)) / 100
		print(actual_allowed_amount,"<------- actual_allowed_amount")
		if len(self.education_allowance_request_details)>0:
			for row in self.education_allowance_request_details:
				print(row.approved_amount,"<------- row.approved_amount",type(row.approved_amount))
				if row.approved_amount:
					if row.approved_amount > row.ed_balance_amount:
						frappe.throw(_("You cannot set approved amount {0}.<br>Your Education Allowance Balance is {1}".format(row.approved_amount,row.ed_balance_amount)))
					if row.approved_amount <= actual_allowed_amount:
						if row.exceed_limit==1:
							frappe.throw(_("# Row {0}: There is no need to exceed the limit of amount. Please uncheck <b>Exceed Limit</b> Checkbox".format(row.idx)))
					else:
						print(actual_allowed_amount, type(actual_allowed_amount), "++++++++++++++actual_allowed_amount", row.approved_amount, type(row.approved_amount), "++++++++++++++row.approved_amount")
						if row.exceed_limit==0:
							frappe.throw(_("# Row {0}: Your approved amount cannot be greater than {1}.<br>If you want to exceed the limit then please check <b>Exceed Limit</b> Checkbox".format(row.idx,flt(actual_allowed_amount,2))))
				if row.exceed_limit==1:
					allow_to_exceed_limit = frappe.db.get_value("Payment Season Details ST",{"payment_season":row.season},"allow_to_exceed")
					if allow_to_exceed_limit == _("No"):
						frappe.throw(_("# Row {0}: You are not allowed to exceed the limit of amount. Please uncheck <b>Exceed Limit</b> Checkbox and decrease the approved amount".format(row.idx)))

	# def calculate_and_validate_approved_amount(self):
	# 	total_approved_amount = 0
	# 	check_against_grade_limit = frappe.db.get_single_value("Stats Settings ST","check_against_grade_limit")
	# 	print(check_against_grade_limit,"---Stats Settings ST")
	# 	if len(self.education_allowance_request_details)>0:
	# 		for row in self.education_allowance_request_details:
	# 			if check_against_grade_limit == 1:
	# 				if self.allowance_limit:
	# 					limit_per_season = self.allowance_limit / 3
	# 					if row.approved_amount > limit_per_season:
	# 						frappe.throw(_("#Row {0} :Your approved amount cannot be greater than {1}".format(row.idx,flt(limit_per_season,2))))
	# 			total_approved_amount = total_approved_amount + row.approved_amount
		
	# 	self.approved_amount = total_approved_amount

	def calculate_unpaid_amount(self):
		previous_allowance_requests = frappe.db.get_all("Education Allowance Request ST",
												  filters={"employee_no":self.employee_no,"educational_year":self.educational_year,"docstatus":1},
												  fields=["name"])
		
		if len(self.education_allowance_request_details)>0:
			for row in self.education_allowance_request_details:
				previous_unpaid = 0
				diff_of_requested_approved = (row.requested_amount or 0) - (row.approved_amount or 0)
				if diff_of_requested_approved >= 0:
					row.present_unpaid = diff_of_requested_approved
				if len(previous_allowance_requests)>0:
					for request in previous_allowance_requests:
						if request.name != self.name:
							unpaid = frappe.db.get_value("Education Allowance Request Details ST",{"parent":request.name,"child_name":row.child_name},"present_unpaid")
							print(unpaid,"unpaid")
							previous_unpaid = previous_unpaid + (unpaid or 0)
					row.previous_unpaid = previous_unpaid
					if diff_of_requested_approved < 0:
						row.total_unpaid = (row.present_unpaid or 0) + previous_unpaid + diff_of_requested_approved
					else :
						row.total_unpaid = (row.present_unpaid or 0) + previous_unpaid
				else:
					row.total_unpaid = row.present_unpaid

	def deduct_allowance_amount_from_employee_profile_in_dependants_table(self):
		education_allowance_amount = frappe.db.get_value("Employee Grade",self.grade,"custom_education_allowance_amount")
		if len(self.education_allowance_request_details)>0:
			for row in self.education_allowance_request_details:
				print("INNNNNNNNNNNNNNNN",row.child_reference)
				### Deduct approved amount from Balance
				### If first request then deduct approved amount from actual amount ( amount from grade )
				### Else deduct from balance in employee dependants table
				
				previous_request_exists = frappe.db.exists("Education Allowance Request Details ST",{"child_reference":row.child_reference,"docstatus":1,"name":["!=",row.name]})
				print(previous_request_exists,"==================previous_request_exists")
				if previous_request_exists != None and previous_request_exists != row.name:
					current_balance_in_employee = frappe.db.get_value("Dependants Details ST",row.child_reference,"employee_education_allowance_balance")
					if current_balance_in_employee>0:
						balance_after_request = current_balance_in_employee - row.approved_amount
					print(current_balance_in_employee,"----current_balance_in_employee",balance_after_request,"----balance_after_request")
					frappe.db.set_value("Dependants Details ST",row.child_reference,"employee_education_allowance_balance",balance_after_request)
				else:
					balance_after_request = education_allowance_amount - row.approved_amount
					frappe.db.set_value("Dependants Details ST",row.child_reference,"employee_education_allowance_balance",balance_after_request)
				frappe.db.set_value("Dependants Details ST",row.child_reference,"applied_for_education_allowance",1)

			employee_doc = frappe.get_doc("Employee",self.employee_no)
			employee_doc.add_comment("Comment",text=_("Education Balance in Dependants Details is updated based on {0}".format(get_link_to_form(self.doctype,self.name))))
			employee_doc.save(ignore_permissions=True)
			frappe.msgprint(_("Education amount is deducted in employee profile."),indicator="green",alert=True)

	
	@frappe.whitelist()
	def get_employee_dependants_history(self):
		employee_edr_history = []
		previous_education_allowance_request_list = frappe.db.get_all("Education Allowance Request ST",
																filters={"docstatus":1,"employee_no":self.employee_no},
																fields=["name"],order_by="creation ASC")
		if len(previous_education_allowance_request_list)>0:
			for row in previous_education_allowance_request_list:
				edr_details = frappe.db.get_all("Education Allowance Request Details ST",
									filters={"parent":row.name},
									fields=["child_name","relation","date_of_birth","age","payment_attachment","requested_amount","approved_amount","ed_due_amount","ed_balance_amount","season","exceed_limit","child_reference"])
				if len(edr_details)>0:
					for detail_row in edr_details:
						employee_edr_history.append(detail_row)
		
		return employee_edr_history

	@frappe.whitelist()
	def get_season_types(self):
		season_details = frappe.db.get_all("Release Education Allowance ST",
									filters={"activate":"Yes","education_year":self.educational_year}, 
									fields=['name'])
		
		season_types = []
		if len(season_details)>0:
			doc = frappe.get_doc("Release Education Allowance ST",season_details[0].name)
			if len(doc.season_type)>0:
				for row in doc.season_type:
					season_types.append(row.season_type)
			
		return season_types
	
	@frappe.whitelist()
	def check_for_pending_amount(self):
		pending_amount = 0
		if len(self.education_allowance_request_details)>0:
			for row in self.education_allowance_request_details:
				if row.requested_amount and row.approved_amount and row.approved_amount < row.requested_amount:
					pending_amount = (row.requested_amount - row.approved_amount)

					return {
						"pending_amount":pending_amount
					}
				
	# @frappe.whitelist()
	# def check_action_is_rejected(self):
	# 	is_rejected = False
	# 	workflow_name = frappe.db.get_value("Workflow",{"document_type":self.doctype,"is_active":1},"name")
	# 	if workflow_name:
	# 		workflow = frappe.get_doc("Workflow",workflow_name)
	# 		current_state = self.workflow_state

	# 		for state in workflow.transitions:
	# 			# print(state.idx, "------------>", state.custom_rejection_reason_require)
	# 			if state.next_state == current_state and state.custom_rejection_reason_require == 1:
	# 				is_rejected = True
	# 				break

	# 	return is_rejected
	
	# @frappe.whitelist()			
	# def add_reject_reason(self,reject_reason):
	# 	self.add_comment("Comment",text="Education Allowance Request is <b>Rejected</b>.<br>Reason: {0}".format(reject_reason))
	# 	self.save(ignore_permissions=True)

	@frappe.whitelist()
	def set_approved_amount(self,employee,grade,season,requested_amount,educational_year,child_reference,ed_balance_amount):
		print("*"*100)
		approved_amount = 0
		due_amount = 0
		total_paid_per_season = get_paid_amount_based_on_educational_year_and_season_per_child(employee,season,educational_year,child_reference)
		
		employee_education_balance_based_on_grade = frappe.db.get_value("Employee Grade",grade,"custom_education_allowance_amount")
		
		payment_percentage = frappe.db.get_value("Payment Season Details ST",{"payment_season":season},"payment_percentage")
		actual_amount_limit = flt((employee_education_balance_based_on_grade * payment_percentage ) / 100, 2)
		remaining_per_season = actual_amount_limit - total_paid_per_season
		
		previous_request_list = frappe.db.sql("""
					SELECT
						edar.name request_name,
						edar.educational_year,
						edar.season,
						edar.employee_no,
						edard.child_name,
						edard.child_reference,
						edard.approved_amount,
						edard.requested_amount,
						edard.ed_due_amount
					FROM
						`tabEducation Allowance Request ST` edar
					INNER JOIN 
						`tabEducation Allowance Request Details ST` edard
					ON
						edar.name = edard.parent
					WHERE 
						edar.docstatus = 1 and edar.educational_year = '{0}' and edar.employee_no = '{2}' and edard.child_reference = '{3}' and edard.ed_due_amount > 0
					ORDER BY edar.creation DESC
					limit 1
				""".format(educational_year, season, employee, child_reference),as_dict=1)
		
		if flt(requested_amount) <= flt(ed_balance_amount):
			if flt(requested_amount) <= actual_amount_limit:
				if len(previous_request_list)>0:
					approved_amount = flt(requested_amount)
					for row in previous_request_list:
						if row.get("ed_due_amount") == None :
							pass
						else:
							if row.get("ed_due_amount") > 0:		
								# if (approved_amount + row.ed_due_amount) < flt(ed_balance_amount):
								if approved_amount + row.ed_due_amount <= remaining_per_season:
									approved_amount = approved_amount + row.ed_due_amount
								else:
									# approved_amount = approved_amount + remaining_per_season
									allow_to_exceed_limit = frappe.db.get_value("Payment Season Details ST",{"payment_season":season},"allow_to_exceed")
									if allow_to_exceed_limit == _("Yes"):
										if approved_amount + row.ed_due_amount <= flt(ed_balance_amount):
											approved_amount = approved_amount + row.ed_due_amount
										else:
											approved_amount = flt(ed_balance_amount)
									else:
										approved_amount = remaining_per_season
							else :
								approved_amount = approved_amount
				else : 
					if flt(requested_amount) >= remaining_per_season:
						approved_amount = remaining_per_season
					else :
						approved_amount = flt(requested_amount)
			else:
				allow_to_exceed_limit = frappe.db.get_value("Payment Season Details ST",{"payment_season":season},"allow_to_exceed")
				if _(allow_to_exceed_limit) == _("Yes"):
					approved_amount = flt(requested_amount)
				if _(allow_to_exceed_limit) == _("No"):
					approved_amount = flt(actual_amount_limit)
		else :
			frappe.throw(_("You cannot request amount greater than Education Allowance Balance {0}".format(ed_balance_amount)))
			# approved_amount = flt(ed_balance_amount)

		if flt(requested_amount) > flt(approved_amount):
			print(flt(requested_amount) > flt(approved_amount), flt(requested_amount) , flt(approved_amount),"++++++++++++++++++++++++++")
			due_amount = flt(requested_amount) - flt(approved_amount)
		else :
			due_amount = 0
		return {
			"approved_amount":approved_amount,
			"ed_due_amount":due_amount
		}

@frappe.whitelist()
def get_employee_dependants(employee, season, educational_year):
	print("+++++++++++++++++++")
	# req_doc = frappe.get_doc("Education Allowance Request ST",docname)
	employee_family_details = []
	employee_doc = frappe.get_doc("Employee", employee)
	print(employee, season, "---------------------------------------------")
	education_allowance_amount = frappe.db.get_value("Employee Grade",employee_doc.grade,"custom_education_allowance_amount")
	if education_allowance_amount == 0:
		frappe.throw(_("Please set Education Allowance Amount in employee grade {0}".format(get_link_to_form("Employee Grade",employee_doc.grade))))
	else :
		if len(employee_doc.custom_dependants)>0:
			for row in employee_doc.custom_dependants:
				employee_child = {}
				# due_amount = 0
				if row.relation in ["Son","Daughter"]:
					child_age = (month_diff(today(),row.date_of_birth))/12
					min_allowed_age, max_allowed_age = frappe.db.get_value("Stats Settings ST",None,["minimum_age_for_education_allowance","maximum_age_for_education_allowance"])
					if child_age > flt(min_allowed_age) and child_age < flt(max_allowed_age):
						employee_child["name"]=row.name1
						employee_child["relation"]=row.relation
						employee_child["date_of_birth"]=row.date_of_birth
						employee_child["age"]=flt(child_age,0)
						employee_child["season"]=season
						employee_child["child_reference"]=row.name
						employee_child["id_number"]=row.id_number

						### Fetch Education Balance amount per child 
						### If employee applies for first time then balance amount is from employee grade
						### If employee applies second time then balance amount is from Employee Dependants table 

						education_allowance_request_exists = frappe.db.exists("Education Allowance Request Details ST",{"child_reference":row.name,"docstatus":1})
						
						if education_allowance_request_exists:
							employee_education_balance = row.employee_education_allowance_balance
						else:
							employee_education_balance = education_allowance_amount

						employee_child["ed_balance_amount"]=employee_education_balance

						### Calculate Due amount based on Previous Requests

						# educational_year_satrt_date, educational_year_end_date = frappe.db.get_value("Educational Year ST",educational_year,["educational_year_start_date","educational_year_end_date"])
						# education_allowance_request_based_on_educational_year = frappe.db.get_all("Education Allowance Request ST",
						# 												filters={"employee_no":employee,"docstatus":1,"creation_date":["between",[educational_year_satrt_date,educational_year_end_date]]},
						# 												fields=["name"])
						
						# if len(education_allowance_request_based_on_educational_year)>0:
						# 	for request in education_allowance_request_based_on_educational_year:
						# 		req_doc = frappe.get_doc("Education Allowance Request ST",request.name)

						# 		payment_percentage = frappe.db.get_value("Payment Season Details ST",{"payment_season":season},"payment_percentage")
						# 		if payment_percentage:
						# 			actual_amount_limit = flt((education_allowance_amount * payment_percentage ) / 100, 2)
									
						# 		else:
						# 			frappe.throw(_("Please set payment percentage in Payment Season Details in {0}".format(get_link_to_form("Stats Settings ST","Stats Settings ST"))))

						# 		if len(req_doc.education_allowance_request_details)>0:
						# 			for req_row in req_doc.education_allowance_request_details:
						# 				if req_row.child_reference==row.name:
						# 					if flt(req_row.requested_amount) > flt(req_row.approved_amount):
						# 						due_amount = due_amount + (flt(req_row.approved_amount) - flt(req_row.requested_amount))
						# 					if (req_row.approved_amount) < flt(actual_amount_limit):
						# 						due_amount = due_amount + (flt(actual_amount_limit) - flt(req_row.approved_amount))
						
						# employee_child["ed_due_amount"]=due_amount
						employee_family_details.append(employee_child)
	print(employee_family_details,"---employee_family_details---")
	return employee_family_details

@frappe.whitelist()
def create_new_request_for_pending_amount(source_name, target_doc=None, doctype=None):
	request_doc = frappe.get_doc(doctype,source_name)
	def set_missing_values(source, target):

		target.creation_date = today()
		release_details = frappe.db.get_list('Release Education Allowance ST', 
									   filters= {"activate": 'Yes',"activate_from":['<=',today()],"activate_till":['>=',today()]},
									   fields= ['season', 'education_year','name'])
		if len(release_details)>0:
			target.release_reference = release_details[0].name
			target.educational_year = release_details[0].education_year
			target.season = release_details[0].season
		
		previous_request_kids = []
		release_education_allowance = frappe.db.get_all("Release Education Allowance ST",
											filters={"activate":_("Yes"),"activate_from":['<=',target.creation_date],"activate_till":['>=',target.creation_date]}, 
											fields=["season", "education_year"])
		print(release_education_allowance,"---release_education_allowance---")
		if len(release_education_allowance)>0:
			for row in release_education_allowance:
				if row.season != request_doc.season:
					target.season = row.season
					target.educational_year = row.education_year
					break
		if len(request_doc.education_allowance_request_details)>0:
			for item in request_doc.education_allowance_request_details:
				### Create new request only for those childs whose requested amount is greater than approved amount
				if item.requested_amount and item.approved_amount and item.requested_amount > item.approved_amount:

					item_row=target.append("education_allowance_request_details",{})
					item_row.child_name = item.child_name
					item_row.relation = item.relation
					item_row.date_of_birth = item.date_of_birth
					item_row.age = item.age
					item_row.child_reference = item.child_reference
					item_row.id_number = item.id_number
					item_row.requested_amount = item.requested_amount - item.approved_amount
					item_row.approved_amount = item.requested_amount - item.approved_amount
					item_row.ed_balance_amount = item.ed_balance_amount - item.approved_amount
					item_row.payment_attachment = item.payment_attachment
					item_row.school_name = item.school_name
					item_row.season_type = item.season_type
					item_row.school_document = item.school_document
					item_row.season = target.season
					item_row.exceed_limit = 0

					previous_request_kids.append(item.child_name)

		other_dependants_data = get_employee_dependants(request_doc.employee_no,request_doc.season,request_doc.educational_year)

		if len(other_dependants_data)>0:
			for child in other_dependants_data:
				if child.get("name") not in previous_request_kids:
					item_row=target.append("education_allowance_request_details",{})
					item_row.child_name = child.get("name")
					item_row.relation = child.get("relation")
					item_row.date_of_birth = child.get("date_of_birth")
					item_row.age = child.get("age")
					item_row.child_reference = child.get("child_reference")
					item_row.id_number = child.get("id_number")
					item_row.ed_balance_amount = child.get("ed_balance_amount")
					item_row.season = target.season
					item_row.exceed_limit = 0

		
	doc = get_mapped_doc('Education Allowance Request ST', source_name, {
			'Education Allowance Request ST': {
				'doctype': 'Education Allowance Request ST',			
				'validation': {
					'docstatus': ['!=', 2]
				}
			},
			"Education Allowance Request Details ST": {
				"doctype": "Education Allowance Request Details ST",
				"condition":lambda doc:len(doc.name)<0,
			},	
		}, target_doc,set_missing_values)
	
	doc.flags.ignore_mandatory = True
	doc.save(ignore_permissions=True)
	frappe.msgprint(_("New request is created {0}").format(doc.name),alert=True)	
	return doc.name

def get_paid_amount_based_on_educational_year_and_season_per_child(employee,season,educational_year,child_reference):
	total_paid_per_season = 0
	other_allowance_request_for_same_season_and_year = frappe.db.sql("""
				SELECT
					edar.name request_name,
					edar.educational_year,
					edar.season,
					edar.employee_no,
					edard.child_name,
					edard.child_reference,
					edard.approved_amount,
					edard.requested_amount,
					edard.ed_due_amount
				FROM
					`tabEducation Allowance Request ST` edar
				INNER JOIN 
					`tabEducation Allowance Request Details ST` edard
				ON
					edar.name = edard.parent
				WHERE 
					edar.docstatus = 1 and edar.educational_year = '{0}' and edar.season = '{1}' and edar.employee_no = '{2}' and edard.child_reference = '{3}'
					""".format(educational_year,season,employee,child_reference), as_dict=1)
	if len(other_allowance_request_for_same_season_and_year)>0:
		for row in other_allowance_request_for_same_season_and_year:
			total_paid_per_season = total_paid_per_season + row.approved_amount
	
	return total_paid_per_season