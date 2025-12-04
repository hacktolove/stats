// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Petty Cash Re-Payment ST", {
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
    },

    onload(frm) {
        if (frm.is_new() || frm.doc.docstatus == 0) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department', 'custom_sub_department'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('created_by', values.employee_name)
                    frm.set_value('main_department', values.department)
                    frm.set_value('sub_department', values.custom_sub_department)
                })
        }
    },

    // refresh(frm) {
    //     if (frm.doc.deposit_to_mof == "Pending" && frm.doc.docstatus == 1) {
    //         frm.add_custom_button(__('Deposit to MOF'), () => create_deposit_to_mof_from_pc_repayment(frm));
    //     }
    // },
});

let create_deposit_to_mof_from_pc_repayment = function (frm) {
    frm.call("create_deposit_to_mof").then(r => {
        let deposit_to_mof = r.message
        frappe.open_in_new_tab = true;
        frappe.set_route("Form", "Deposit To MOF ST", deposit_to_mof);
    })
}