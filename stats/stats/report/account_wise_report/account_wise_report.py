# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from erpnext.accounts.report.budget_variance_report.budget_variance_report import execute as budget_variance_report

def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		frappe.msgprint(_("No records found"))
		return columns, data
	
	return columns, data


def get_columns(filters):
	columns = [
		{
			"fieldname": "account_name",
			"fieldtype": "Link",
			"label": _("Account Name"),
			"options": "Account",
			"width": 200
		},
		{
			"fieldname": "classifications",
			"fieldtype": "Data",
			"label": _("Classifications"),
			"width": 200
		},
		{
			"fieldname": "economic_no",
			"fieldtype": "Data",
			"label": _("Economic No"),
			"width": 200
		},
		{
			"fieldname": "total_approved_amount",
			"fieldtype": "Currency",
			"label": _("Total Approved Amount"),
			"width": 200
		},
		# {
		# 	"fieldname": "budget_approved_amount",
		# 	"fieldtype": "Currency",
		# 	"label": _("Buget Approved Amount"),
		# 	"width": 200
		# },
		{
			"fieldname": "consumed_amount",
			"fieldtype": "Currency",
			"label": _("Consumed Amount"),
			"width": 200
		},
		{
			"fieldname": "remaining_amount",
			"fieldtype": "Currency",
			"label": _("Remaining Amount"),
			"width": 200
		},
		{
			"fieldname": "booked_amount",
			"fieldtype": "Currency",
			"label": _("Booked Amount"),
			"width": 200
		},
		{
			"fieldname": "final_remaining_amount",
			"fieldtype": "Currency",
			"label": _("Final Remaining Amount"),
			"width": 200
		}
	]

	if filters.get('cost_center_wise') == 1:
		columns.insert(0, {
			"fieldname": "cost_center",
			"label":_("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 200
		})
		
	return columns

def get_conditions(filters):
	conditions =""

	if filters.fiscal_year:
		conditions += " b.fiscal_year = '{0}'".format(filters.fiscal_year)

	if filters.cost_center:
		conditions += "and b.cost_center = '{0}'".format(filters.cost_center)
	
	return conditions

def get_data(filters):
	data = []

	budget_details = get_budget_details_from_variance_report(filters)
	
	if filters.get('cost_center_wise') == 1:

		for budget_row in budget_details:
			account = frappe.db.get_value('Account', budget_row[1], ['custom_classifications', 'custom_economic_number'], as_dict=1)

			if filters.cost_center:
				if filters.cost_center == budget_row[0]:
					data.append({
						"cost_center": budget_row[0],
						"account_name": budget_row[1],
						"classifications": account.custom_classifications or '',
						"economic_no": account.custom_economic_number or '',
						"total_approved_amount": budget_row[2],
						"consumed_amount": budget_row[3],
						"remaining_amount": budget_row[4],
						"booked_amount":1000
					})
				else:
					continue
			else:
				data.append({
						"cost_center": budget_row[0],
						"account_name": budget_row[1],
						"classifications": account.custom_classifications or '',
						"economic_no": account.custom_economic_number or '',
						"total_approved_amount": budget_row[2],
						"consumed_amount": budget_row[3],
						"remaining_amount": budget_row[4],
						"booked_amount":1000
					})
			

	else:
		data = frappe.db.sql("""
			SELECT
				dba.budget_expense_account AS account_name,
				acc.custom_classifications AS classifications,
				acc.custom_economic_number AS economic_no,
				SUM(dba.approved_amount) AS total_approved_amount
			FROM
				`tabAccumulative Budget ST` AS ab
			INNER JOIN `tabDepartment Wise Budget Allocation Details ST` AS dba ON
				dba.parent = ab.name
			INNER JOIN `tabAccount` AS acc ON
				acc.name = dba.budget_expense_account
			WHERE
				ab.fiscal_year = {0}
			GROUP BY
				dba.budget_expense_account
			""".format(filters.get('fiscal_year')), debug=1,as_dict=1)
		
		

		for data_row in data:
			# total_approved_amt = 0
			total_consumed_amt = 0
			total_remaining_amt = 0
			for budget_row in budget_details:
				print(budget_row[1], "========budget_row[1]")
				if data_row.account_name == budget_row[1]:
					# total_approved_amt = total_approved_amt + budget_row[2]
					total_consumed_amt = total_consumed_amt + budget_row[3]
					total_remaining_amt = total_remaining_amt + budget_row[4]
				else:
					pass
			
			data_row.update({'consumed_amount': total_consumed_amt, 'remaining_amount': total_remaining_amt})
	
	return data


def get_budget_details_from_variance_report(filters,account=None):
	company = erpnext.get_default_company()
	print(company, "====company===")

	report_filters = frappe._dict({
		'from_fiscal_year': filters.get('fiscal_year'),
		'to_fiscal_year': filters.get('fiscal_year'),
		'period':'Yearly',
		'company': company,
		'budget_against': 'Cost Center',
	})

	report_data = budget_variance_report(report_filters)
	# print(report_data[1])

	return report_data[1]
