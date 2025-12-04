frappe.ui.form.on("Company", {
    setup(frm) {
        frm.set_query("custom_business_trip_budget_expense_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": ["in",["Expense Account", "Indirect Expense"]]
                }
            };
        })
        frm.set_query("custom_business_trip_budget_chargeable_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": "Chargeable"
                }
            };
        })
        frm.set_query("custom_reallocation_budget_expense_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": ["in",["Expense Account", "Indirect Expense"]]
                }
            };
        })
        frm.set_query("custom_reallocation_budget_chargeable_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": "Chargeable"
                }
            };
        })

        frm.set_query("custom_overtime_budget_expense_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": ["in",["Expense Account", "Indirect Expense"]]
                }
            };
        })
        frm.set_query("custom_overtime_budget_chargeable_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": "Chargeable"
                }
            };
        })
        frm.set_query("custom_default_salary_expense_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": ["in",["Expense Account", "Indirect Expense"]]
                }
            };
        })
        frm.set_query("custom_default_debit_account_mof", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0
                }
            };
        })
        frm.set_query("custom_default_revenue_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0
                }
            };
        })
        frm.set_query("custom_default_central_bank_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0
                }
            };
        })
        frm.set_query("custom_default_payment_order_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0
                }
            };
        })
        frm.set_query("custom_default_employee_petty_cash_account", function (doc) {
            return {
                filters: {
                    "account_type": "Payable",
                    "company": frm.doc.name,
                    "is_group": 0
                }
            };
        })
        frm.set_query("custom_default_international_subscription_expense_account", function (doc) {
            return {
                filters: {
                    "account_type": ["in",["Expense Account", "Indirect Expense"]],
                    "company": frm.doc.name,
                    "is_group": 0
                }
            };
        })
        frm.set_query("custom_default_international_subscription_chargeable_account", function (doc) {
            return {
                filters: {
                   "account_type": "Chargeable",
                   "company": frm.doc.name,
                   "is_group": 0
                }
            };
        })
        frm.set_query("custom_annual_reward_expense_account", function (doc) {
            return {
                filters: {
                    "account_type": ["in",["Expense Account", "Indirect Expense"]],
                    "company": frm.doc.name,
                    "is_group": 0
                }
            };
        })
        frm.set_query("custom_annual_reward_chargeable_account", function (doc) {
            return {
                filters: {
                   "account_type": "Chargeable",
                   "company": frm.doc.name,
                   "is_group": 0
                }
            };
        })
        frm.set_query("custom_default_vacation_allocated_account", function (doc) {
            return {
                filters: {
                   "account_type": "Chargeable",
                   "company": frm.doc.name,
                   "is_group": 0
                }
            };
        })
        frm.set_query("custom_default_end_of_service_allocated_account", function (doc) {
            return {
                filters: {
                   "account_type": "Chargeable",
                   "company": frm.doc.name,
                   "is_group": 0
                }
            };
        })
        frm.set_query("custom_education_allowance_expense_account", function (doc) {
            return {
                filters: {
                    "account_type": ["in",["Expense Account", "Indirect Expense"]],
                    "company": frm.doc.name,
                    "is_group": 0
                }
            };
        })
        frm.set_query("custom_education_allowance_chargeable_account_", function (doc) {
            return {
                filters: {
                   "account_type": "Chargeable",
                   "company": frm.doc.name,
                   "is_group": 0
                }
            };
        })
        frm.set_query("custom_default_pending_income_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": "Income Account"
                }
            };
        })
        frm.set_query("custom_penalty_income_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": "Income Account"
                }
            };
        })
    }
})