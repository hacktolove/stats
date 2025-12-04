# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class StatisticRequestST(Document):
	def validate(self):
		self.calculate_costs()

	def calculate_costs(self):
		# worker_cost_per_day = frappe.db.get_single_value('Stats Settings ST', 'worker_cost_per_day')
		# if not worker_cost_per_day or worker_cost_per_day < 1:
		# 	frappe.throw(_("Please Set Worker Cost Per Day In Stats Settings."))
		# else:
		# 	pass

		employee_cost_per_day = frappe.db.get_single_value('Stats Settings ST', 'employee_cost_per_day')
		if not employee_cost_per_day or employee_cost_per_day < 1:
			frappe.throw(_("Please Set Employee Cost Per Day In Stats Settings."))
		else:
			pass

		reservation_cost = frappe.db.get_single_value('Stats Settings ST', 'reservation_cost')
		if not reservation_cost or reservation_cost < 1:
			frappe.throw(_("Please Set Reservation Cost Per Day In Stats Settings."))
		else:
			pass

		self.form_filling_duration = (self.question_time_in_second / 60) * self.form_question_no
		print(self.contract_time,type(self.contract_time),"self.contract_time")
		if self.contract_time > 0 and self.no_of_visits:
			self.researcher_share = ((((self.question_time_in_second * 60) + (self.average_trip_duration or 0))
								/ (self.average_trip_duration or 0 + self.form_filling_duration)) * (self.contract_time or 0)) / self.no_of_visits

		if self.researcher_share>0:
			self.no_of_researchers_based_on_sample = self.no_of_sample / self.researcher_share

		self.no_of_researchers = self.no_of_researchers_based_on_sample * (self.reduce_rate - 1)

		self.no_of_inspectors = self.no_of_researchers / 5

		self.total_no_team = ((self.no_of_researchers or 0) + (self.no_of_inspectors or 0)
							+ (self.no_of_support_team or 0)+ (self.no_of_supervisor or 0))
		
		self.employee_cost = self.total_no_team * employee_cost_per_day * self.contract_time

		self.estimated_cost = self.total_no_team * employee_cost_per_day * self.contract_time

		self.reservation_value = self.estimated_cost * (reservation_cost / 100)

		self.final_cost = self.estimated_cost + self.reservation_value

		self.number_of_reserve_workers = self.total_no_team * (reservation_cost / 100)