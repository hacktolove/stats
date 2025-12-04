// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("PO Payment Schedule ST", {

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
        });

        frm.set_query("budget_account","payment_details", function() {
            return {
                query: "stats.api.get_po_budget_account",
                filters: {
                    "po_name": frm.doc.po_reference
                }
            };
        });
    },

    onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department', 'custom_sub_department'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('created_by', values.employee_name)
                    frm.set_value('main_department', values.department)
                    frm.set_value('sub_department', values.custom_sub_department)
                })
        }
    },
});
