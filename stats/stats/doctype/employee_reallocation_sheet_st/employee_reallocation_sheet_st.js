// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Reallocation Sheet ST", {
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
    },

    onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
                .then(r => {
                    let values = r.message;
                    frm.set_value('employee_no', values.name)
                })
        }
    },

    fetch_reallocation_request(frm){
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }
        
        frm.set_value("employee_reallocation_request_details", "");
        frm.call("fetch_employee_reallocation_request").then((r) => {
            let available_training_request_list = r.message
            if (available_training_request_list.length > 0){
                available_training_request_list.forEach((ele) => {
                    var d = frm.add_child("employee_reallocation_request_details");
                    frappe.model.set_value(d.doctype, d.name, "reallocation_reference", ele.name)
                })
                frm.refresh_field('employee_reallocation_request_details')
                frm.save()
            }
        })
    }
});
