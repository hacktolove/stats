# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, add_to_date, get_datetime, get_date_str, cstr, getdate
from stats.hr_utils import check_if_holiday_between_applied_dates
from hrms.hr.doctype.employee_checkin.employee_checkin import time_diff_in_hours

class TrainingRequestST(Document):

	def on_update_after_submit(self):
		if self.training_method == "Attendance" and self.employee_checkin_required == "No" and self.employee_checkout_required == "No":
			self.create_future_attendance_for_training()

	def create_future_attendance_for_training(self):
		if self.status == "Accepted":
			days = date_diff(self.training_end_date,self.training_start_date)
			different_years_list = []
			for fiscal_year in range ((self.training_start_date).year, (self.training_end_date).year+1):
				if fiscal_year not in different_years_list:
					different_years_list.append(fiscal_year)

			yearly_holiday_list = []
			
			for year in different_years_list:
				holiday = {}
				fiscal_year_doc = frappe.get_doc("Fiscal Year",year)
				exist_holiday_list = frappe.db.get_all("Holiday List",
											filters={"to_date":fiscal_year_doc.year_end_date,"from_date":fiscal_year_doc.year_start_date},
											fields=["name"])
				if len(exist_holiday_list)<1:
					frappe.throw(_("Holiday list for year <b>{0}</b> does not exists. Hence we cannot create future attendance.").format(year))
				else :
					holiday["year"]=year
					holiday["holiday_list"]=exist_holiday_list[0].name
					yearly_holiday_list.append(holiday)
			
			for day in range (days+1):
				attendance_date = add_to_date(self.training_start_date,days=day)

				check_holiday = None
				for ele in yearly_holiday_list:
					if attendance_date.year == ele.get("year"):
						check_holiday = check_if_holiday_between_applied_dates(self.employee_no,attendance_date,attendance_date,holiday_list=ele.get("holiday_list"))

				if check_holiday == False:
					attendance_doc = frappe.new_doc("Attendance")
					attendance_doc.employee = self.employee_no
					attendance_doc.attendance_date = attendance_date
					attendance_doc.custom_attendance_type = "In Training"

					employee_shift = frappe.db.get_value("Employee",self.employee_no,"default_shift")
					shift_start_time = frappe.db.get_value("Shift Type",employee_shift,"start_time")
					shift_end_time = frappe.db.get_value("Shift Type",employee_shift,"end_time")

					in_time = get_datetime(get_date_str(attendance_date) + " " + cstr(shift_start_time))
					out_time = get_datetime(get_date_str(attendance_date) + " " + cstr(shift_end_time))
					total_working_hours = time_diff_in_hours(in_time, out_time)

					attendance_doc.shift = employee_shift
					attendance_doc.in_time = in_time
					attendance_doc.out_time = out_time
					attendance_doc.working_hours = total_working_hours
					attendance_doc.status = "Present"
					attendance_doc.save(ignore_permissions=True)
					attendance_doc.submit()
				else :
					pass

			frappe.msgprint(_("Attendance from {0} to {1} is created.").format(self.training_start_date,self.training_end_date),alert=True)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_training_events(doctype, txt, searchfield, start, page_len, filters):
	employee_no = filters.get("employee_no")
	request_date = filters.get("request_date")
	employee_main_department, employee_sub_department = frappe.db.get_value("Employee",employee_no,["department","custom_sub_department"])
	training_specialized_for_main_department = frappe.db.get_all("Training Event ST",
															filters={"training_status":"Open","targeted_group":"Main Department","main_department":employee_main_department,"name": ("like", f"{txt}%")},
															fields=["name"])
	
	training_specialized_for_sub_department = frappe.db.get_all("Training Event ST",
															filters={"training_status":"Open","targeted_group":"Sub Department","sub_department":employee_sub_department,"name": ("like", f"{txt}%")},
															fields=["name"])
	
	training_specialized_for_group_of_employee = frappe.db.get_all("Training Event ST",
															filters={"training_status":"Open","targeted_group":"Special Employee Group","name": ("like", f"{txt}%")},
															fields=["name"])
	final_training_event_list_for_special_employee = []
	if len(training_specialized_for_group_of_employee)>0:
		for event in training_specialized_for_group_of_employee:
			training_event_doc = frappe.get_doc("Training Event ST",event.name)
			if len(training_event_doc.training_special_employee_details)>0:
				for row in training_event_doc.training_special_employee_details:
					if row.employee_no == employee_no:
						final_training_event_list_for_special_employee.append(event)
	
	training_event_list_for_all = frappe.db.get_all("Training Event ST",
												filters={"training_status":"Open","targeted_group":"","name": ("like", f"{txt}%")},
												fields=["name"])

	all_training_event = final_training_event_list_for_special_employee + training_specialized_for_main_department + training_specialized_for_sub_department + training_event_list_for_all

	final_events = ()
	if len(all_training_event) > 0:
		for training_event in all_training_event:
			training_announcement_name = frappe.db.get_value("Training Announcement Details ST",{"training_event":training_event.name},["parent"])
			if training_announcement_name:
				apply_start_date, apply_end_date = frappe.db.get_value("Training Announcement Details ST",{"training_event":training_event.name,"parent":training_announcement_name},["apply_start_date", "apply_end_date"])
				if apply_start_date and apply_end_date:
					if getdate(request_date) >= getdate(apply_start_date) and getdate(request_date) <= getdate(apply_end_date):
						final_event_name = (training_event.name,)
						final_events += (final_event_name,)

	return final_events