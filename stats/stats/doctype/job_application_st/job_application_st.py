# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, cint,getdate
# from hijridate import Hijri, Gregorian

class JobApplicationST(Document):
	def validate(self):
		self.validate_national_id_no()
		# enable_hijri_date = frappe.db.get_single_value('Stats Settings ST', 'enable_hijri_date')
		# if enable_hijri_date == 1:
		# 	self.hijri_birth_date=self.set_date_in_hijri(self.date_of_birth)

	# def set_date_in_hijri(self,date_of_birth) :
	# 	# https://hijri-converter.readthedocs.io/en/stable/usage.html
	# 	# https://datehijri.com/en/
	# 	gregorian_splits=date_of_birth.split('-')
	# 	year_split=cint(gregorian_splits[0])
	# 	month_split=cint(gregorian_splits[1])
	# 	day_split=cint(gregorian_splits[2])
	# 	dob_hijri= Gregorian(year_split,month_split,day_split).to_hijri()
	# 	dobj_hijri_iso=dob_hijri.isoformat()
	# 	dobj_hijri_tuple=dob_hijri.datetuple()
	# 	readable_hijri= dob_hijri.month_name()+" "+cstr(dobj_hijri_tuple[2])+","+cstr(dobj_hijri_tuple[0])+" "+dob_hijri.notation()
	# 	hijri_date = dobj_hijri_iso+" "+readable_hijri
	# 	final_hijri_date = (hijri_date[:140]) if len(hijri_date) > 140 else hijri_date
	# 	return final_hijri_date



	def validate_national_id_no(self):
		if self.id_igama_no:
			national_id = cstr(self.id_igama_no)

			if len(national_id) != 10:
				frappe.throw(_("Iqama/National ID No Must Be 10 Digits"))
