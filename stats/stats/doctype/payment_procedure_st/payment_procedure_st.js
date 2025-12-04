// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Procedure ST", {
    setup(frm) {
        frm.set_query("budget_account", function (doc) {
            return {
                query: "stats.stats.doctype.department_budget_st.department_budget_st.get_budget_account",
            };
        })
    },
	party_type(frm){
        if (frm.doc.party_type == "Employee"){
            frm.set_value("party_name_employee","Multiple Payment")
        }
    },
    payment_type(frm){
        if (frm.doc.payment_type == __("Indirect Payment")) {
            const default_company = frappe.defaults.get_default("company");
            frappe.db.get_value('Company', default_company, 'default_bank_account')
                .then(r => {
                let default_bank_account = r.message.default_bank_account
                frm.set_value("middle_bank_account",default_bank_account)
            })
        }
    }
});
