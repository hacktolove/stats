// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Request ST", {
    setup(frm) {
        const default_company = frappe.defaults.get_default("company");
        frm.set_query("budget_account", function (doc) {
            return {
                query: "stats.stats.doctype.department_budget_st.department_budget_st.get_budget_account",
            };
        });

        frm.set_query("default_expense_account", function (doc) {
            return {
                filters: {
                    "account_type": ["in",["Expense Account", "Indirect Expense"]],
                    "company": default_company,
                    "is_group": 0
                }
            };
        });

        frm.set_query("default_chargeable_account", function (doc) {
            return {
                filters: {
                   "account_type": "Chargeable",
                   "company": default_company,
                   "is_group": 0
                }
            };
        })
    },
    party_type(frm){
        if (frm.doc.party_type == "Employee"){
            frm.set_value("party_name_employee","Multiple Payment")
        }
    },
});
