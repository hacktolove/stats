// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("International Subscription Payment Request ST", {

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
    
    refresh(frm) {
        if (frm.doc.certificate_status == "Pending" && frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Achievement Certificate'), () => create_achievement_certificate_from_isp(frm));
        }
    },
});

let create_achievement_certificate_from_isp = function (frm) {
    frm.call("create_achievement_certificate").then(r => {
        let certificate_name = r.message
        frappe.open_in_new_tab = true;
        frappe.set_route("Form", "Achievement Certificate ST", certificate_name);
    })
}