// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Petty Cash Request ST", {
    setup(frm) {
        frm.set_query("main_department", function (doc) {
            return {
                query: "stats.api.get_main_department",
            };
        });
        frm.set_query("sub_department", function (doc) {
            if (frm.doc.main_department) {
                return {
                    filters: {
                        parent_department: frm.doc.main_department,
                        is_group: 0
                    }
                };
            }
        })
        frm.set_query("account_name", "pc_request_account_details", function (doc) {
            return {
                filters: {
                    "account_type": "Direct Expense",
                    "is_group": 0
                },
            };
        });
    },

    onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'employee_name')
                .then(r => {
                    let values = r.message;
                    frm.set_value('created_by', values.employee_name)
                })
        }
    },

    refresh(frm) {
        if (frm.doc.loan_status == "Open" && frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Petty Cash Closing'), () => create_petty_cash_closing_from_pc_request(frm));
        }
    },
});

let create_petty_cash_closing_from_pc_request = function (frm) {
    frm.call("create_petty_cash_closing").then(r => {
        let pc_closing = r.message
        frappe.open_in_new_tab = true;
        frappe.set_route("Form", "Petty Cash Closing ST", pc_closing);
    })
}