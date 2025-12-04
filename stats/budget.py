import frappe
from frappe import _



def get_budget_account_details(budget_cost_center,budget_expense_account,fiscal_year):
    filters={
        'budget_cost_center':budget_cost_center,
        'budget_expense_account':budget_expense_account,
        'fiscal_year':fiscal_year
        }
    budget_details = frappe.db.sql(
        """
            select
                            b.cost_center,
                            ba.account,
                            ba.budget_amount as approved,
                            IF(sum(gl.debit), sum(gl.debit)-sum(gl.credit),0) as used,
                            IF(sum(gl.debit),ba.budget_amount-sum(gl.debit)-sum(gl.credit),ba.budget_amount) as available, 
                            b.fiscal_year
            from
                            `tabBudget` b
                            inner join 
                            `tabBudget Account` ba
                            on  b.name = ba.parent and b.docstatus = 1
                            left join    `tabGL Entry` gl
                            on ba.account = gl.account 
                            and b.cost_center = gl.cost_center 
                            and gl.fiscal_year = %(fiscal_year)s
                            and gl.account = %(budget_expense_account)s              
            where           b.cost_center =  %(budget_cost_center)s      
            group by
                gl.name
        """,filters,as_dict=1,debug=1)
    
    print(budget_details)
    if len(budget_details)>0:
        return budget_details[0]
    else:
        return None


def get_budget_account_details_without_cost_center(budget_expense_account,fiscal_year):
    filters={
        'budget_expense_account':budget_expense_account,
        'fiscal_year':fiscal_year
        }
    budget_details = frappe.db.sql(
        """
        select
            gl.account,
            ba.budget_amount as approved,
            IF(sum(gl.debit), sum(gl.debit)-sum(gl.credit),0) as used,
            IF(sum(gl.debit),ba.budget_amount-sum(gl.debit)-sum(gl.credit),ba.budget_amount) as available, 
            b.fiscal_year
        from
            `tabBudget` b
            inner join 
            `tabBudget Account` ba
            on  b.name = ba.parent and b.docstatus = 1
            left join `tabGL Entry` gl
            on ba.account = gl.account 
            and b.cost_center = gl.cost_center 
            and gl.fiscal_year = b.fiscal_year
            and gl.account = ba.account
        WHERE
            ba.account = %(budget_expense_account)s and b.fiscal_year = %(fiscal_year)s
            group by
                gl.name
        """,filters,as_dict=1,debug=1)
    
    print(budget_details)
    if len(budget_details)>0:
        return budget_details[0]
    else:
        return None