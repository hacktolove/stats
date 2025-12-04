# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _

def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_("No records found"))
		return columns, data
	
	return columns, data

def get_columns(filters):
	columns = [
		{
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"label": _("Cost Center"),
			"options": "Cost Center",
			# "hidden":1,
			"width": 200
		},
		{
			"fieldname": "department",
			"fieldtype": "Link",
			"label": _("Department"),
			"options": "Department",
			# "hidden":1,
			"width": 200
		},
		{
			"fieldname": "account",
			"fieldtype": "Link",
			"label": _("Account"),
			"options": "Account",
			# "hidden":1,
			"width": 200
		},
		# {
		# 	"fieldname": "budget",
		# 	"fieldtype": "Link",
		# 	"label": _("Budget"),
		# 	"options": "Budget",
		# 	# "hidden":1,
		# 	"width": 200
		# },
		{
			"fieldname": "approved",
			"fieldtype": "Float",
			"label": _("Approved"),
			"width": 200
		},
		{
			"fieldname": "used",
			"fieldtype": "Float",
			"label": _("Used"),
			"width": 200
		},
		{
			"fieldname": "available",
			"fieldtype": "Float",
			"label": _("Available"),
			"width": 200
		},

	]
	return columns

def get_conditions(filters):
	conditions =""

	if filters.fiscal_year:
		conditions += " b.fiscal_year = '{0}'".format(filters.fiscal_year)

	if filters.cost_center:
		conditions += "and b.cost_center = '{0}'".format(filters.cost_center)
	
	if filters.account:
		conditions += " and ba.account = '{0}'".format(filters.account)
	
	return conditions

def get_data(filters):
	data = []
	conditions = get_conditions(filters)
	print(filters, '===filters')

	data = frappe.db.sql(
		"""SELECT
			b.cost_center,
			dp.name as department,
            ba.account,
            ba.budget_amount as approved,
			IF(sum(gl.debit), sum(gl.debit)-sum(gl.credit),0) as used,
			IF(sum(gl.debit),ba.budget_amount-sum(gl.debit)-sum(gl.credit),ba.budget_amount) as available,
			b.fiscal_year
		FROM
			`tabBudget` b
            inner join 
            `tabBudget Account` ba
            on  b.name = ba.parent and b.docstatus = 1
            and b.fiscal_year = {0}
			inner join
			`tabDepartment` dp
			on b.cost_center = dp.custom_department_cost_center                      
            left join    `tabGL Entry` gl
            on ba.account = gl.account 
            and b.cost_center = gl.cost_center 
		where {1}
		group by gl.name
		order by b.cost_center,ba.account
		""".format(filters.get('fiscal_year'), conditions),filters,as_dict=1)

	return data