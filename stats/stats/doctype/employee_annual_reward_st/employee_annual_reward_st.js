// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Annual Reward ST", {
    onload(frm) {
        // if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department', 'custom_sub_department'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('created_by', values.employee_name)
                    frm.set_value('main_department', values.department)
                    frm.set_value('sub_department', values.custom_sub_department)
                })
        // }
    },

    fetch_employee(frm){

        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("employee_annual_reward_details", "");
        frm.call("fetch_employee_based_on_classification").then(r => {
            let employees = r.message
            console.log(employees,"--------------")
            if (employees.length > 0) {
                employees.forEach((ele) => {
                    var d = frm.add_child("employee_annual_reward_details");
                    frappe.model.set_value(d.doctype, d.name, "employee_no", ele.employee_no)
                    frappe.model.set_value(d.doctype, d.name, "evaluation_classification", ele.evaluation_classification)
                    frappe.model.set_value(d.doctype, d.name, "final_evaluation", ele.final_evaluation)
                })
                frm.refresh_field('employee_annual_reward_details')
                frm.save()
            }
        })
    },
});
