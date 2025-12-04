// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Acting ST", {
    setup(frm) {
        frm.set_query("new_main_department", function (doc) {
            return {
                query: "stats.api.get_main_department",
            };
        });
        frm.set_query("new_sub_department", function (doc) {
            if (frm.doc.new_main_department) {
                return {
                    filters: {
                        parent_department: frm.doc.new_main_department,
                        is_group: 0
                    }
                };
            }
        })
    },

    onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('request_by', values.employee_name)
                    frm.set_value('main_department', values.department)
                })
        }
    },
});
