// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Alternatives ST", {
    onload(frm) {
        // if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('request_by', values.employee_name)
                    frm.set_value('main_department', values.department)
                })
        // }
        frm.set_query("employee_main_department", function (frm) {
            return {
                query: "stats.api.get_main_department",
            };
        })
    },

    fetch_employees(frm){

        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("employee_alternatives_details", "");
        frm.call("fetch_employees_based_on_filters").then(r => {
            let employee_list = r.message
            console.log(employee_list,"--------------")
            if (employee_list.length > 0) {
                employee_list.forEach((ele) => {
                    var d = frm.add_child("employee_alternatives_details");
                    frappe.model.set_value(d.doctype, d.name, "employee_no", ele.employee_no)
                    frappe.model.set_value(d.doctype, d.name, "previous_year_evaluation", ele.previous_year_evaluation)
                    frappe.model.set_value(d.doctype, d.name, "current_year_evaluation", ele.current_year_evaluation)
                    frappe.model.set_value(d.doctype, d.name, "employee_psychometric_test_score", ele.employee_psychometric_test_score)
                })
                frm.refresh_field('employee_alternatives_details')
                frm.save()
            }
        })
    },
});
