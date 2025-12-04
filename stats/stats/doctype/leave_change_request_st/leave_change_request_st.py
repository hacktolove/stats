# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, get_link_to_form, add_to_date, nowdate

class LeaveChangeRequestST(Document):
	def validate(self):
		self.validate_leave_dates()
		# self.create_leave_application()

	def before_submit(self):
		if self.change_type:
			self.leave_application_reference_ro = self.leave_application_reference
			self.leave_application_reference = ''

	def on_submit(self):
		self.create_leave_application()

	def validate_leave_dates(self):
		la = frappe.get_doc('Leave Application', self.leave_application_reference)
		# from_date, to_date, = frappe.db.get_value('Leave Application', self.leave_application_reference, ['from_date','to_date', 'leave_type'])

		if self.change_type == 'Extend' and getdate(self.extend_date) <= getdate(la.to_date):
			frappe.throw(_("Extend Date must be after Leave Application {0} End Date.").format(getdate(la.to_date)))
		elif self.change_type == 'Stop Vacation' and getdate(self.stop_date) >= getdate(la.to_date):
				frappe.throw(_("Vacation Stop Date must be Before Leave Application {0} End Date.").format(getdate(la.to_date)))
		elif self.change_type == 'Cancel' and la.from_date <= getdate(nowdate()):
			frappe.throw(_("You can't cancel after Leave start date {0}. <br> Note: You can use stop vacation.").format(la.from_date))

		if (self.change_type == 'Extend' or self.change_type == 'Stop Vacation') and ( (self.extend_date and getdate(self.extend_date) <= getdate(la.from_date)) or (self.stop_date and getdate(self.stop_date) <= getdate(la.from_date)) ):
			frappe.throw(_("Leave Stats From {0} Date").format(getdate(la.from_date)))

		####  check less days for stop vacation
		if self.change_type == 'Stop Vacation':
			less_days = frappe.db.get_value('Leave Type', la.leave_type, 'custom_less_days_to_stop_leave')

			if less_days and less_days > 0:
				less_days_date = add_to_date(getdate(la.from_date), days=less_days)
				# print(less_days_date, "=========less_days_date")
				if less_days_date >= getdate(self.stop_date):
					frappe.throw(_("You cannot stop leave before {0}").format(less_days_date))

	def create_leave_application(self):
		# to_date = frappe.db.get_value('Leave Application', self.leave_application_reference_ro, 'to_date')
		leave_application = frappe.get_doc('Leave Application', self.leave_application_reference_ro)
		doc = frappe.copy_doc(leave_application)

		if self.change_type == 'Extend':
			doc.workflow_state = ''
			doc.from_date = add_to_date(getdate(leave_application.to_date), days=1)
			doc.to_date = self.extend_date
			doc.posting_date = nowdate()	
			doc.save(ignore_permissions=True)
			
			frappe.msgprint(_("Leave Application {0} is created."
				.format(get_link_to_form('Leave Application', doc.name))), alert=True)
			doc.submit()
		
		elif self.change_type == 'Stop Vacation':
			doc.workflow_state = ''
			doc.to_date = self.stop_date
			doc.posting_date = nowdate()
			
			print(self.leave_application_reference, "======self.leave_application_reference")

			leave_application.workflow_state = 'Cancelled'
			leave_application.cancel()
			
			doc.save(ignore_permissions=True)
			frappe.msgprint(_("Leave Application {0} is created."
				.format(get_link_to_form('Leave Application', doc.name))), alert=True)
			frappe.msgprint(_("Leave Application {0} is cancelled."
				.format(get_link_to_form('Leave Application', leave_application.name))), alert=True)
			doc.submit()

		elif self.change_type == 'Cancel':
			leave_application.workflow_state = 'Cancelled'
			leave_application.cancel()
			frappe.msgprint(_("Leave Application {0} is cancelled."
				.format(get_link_to_form('Leave Application', leave_application.name))), alert=True)
