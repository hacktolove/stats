# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, add_to_date
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday

class EventST(Document):
	pass

@frappe.whitelist()
def calculate_event_days(event_start_date, event_end_date, ignore_holidays_in_number_of_days):
	days = date_diff(getdate(event_end_date), getdate(event_start_date))
	
	if int(ignore_holidays_in_number_of_days) == 1:
		company = erpnext.get_default_company()
		holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")
		no_of_holidays = 0
		if holiday_list != None:
			for i in range(0, days+1):
				event_date = add_to_date(getdate(event_start_date), days=i)
				isHoliday = is_holiday(holiday_list, event_date)
				if isHoliday == True:
					no_of_holidays = no_of_holidays + 1
			days = days - no_of_holidays

	return days+1
		
