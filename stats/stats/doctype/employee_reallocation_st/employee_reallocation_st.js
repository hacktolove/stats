// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Reallocation ST", {
    setup(frm) {
        frm.set_query("new_main_department", function (doc) {
            return {
                query: "stats.api.get_main_department",
            };
        });
        frm.set_query("new_sub_department", function (doc) {
                return {
                    filters: {
                        // parent_department: frm.doc.new_main_department,
                        is_group: 0
                    }
                };
        });
        frm.set_query("assign_current_tasks_to", function (doc) {
            if (frm.doc.main_department) {
                return {
                    query: "stats.stats.doctype.employee_reallocation_st.employee_reallocation_st.get_employee_based_on_main_department",
                    filters: {
                        main_department: frm.doc.main_department
                    }
                };
            }
        })
    },

    onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
                .then(r => {
                    let values = r.message;
                    frm.set_value('employee_no', values.name)
                    if (values.name) {
                        frappe.db.get_value("Employee", values.name, "employee_name")
                            .then(resopnse => {
                                let full_name = resopnse.message.employee_name
                                frm.set_value("created_by", full_name)
                                frm.set_value("assign_current_tasks_to", "")
                            })
                    }
                })
        }
    }
});
