// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Employee Onboarding Template ST", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on("Employee Boarding Activity ST", {
    // user(frm, cdt, cdn) {
    //     let row = locals[cdt][cdn]
    //     if (row.user) {
    //         frappe.db.get_value('Employee', { user_id: row.user }, ['name', 'employee_name'])
    //             .then(r => {
    //                 let values = r.message;
    //                 frappe.model.set_value(cdt, cdn, 'direct_manager', values.name);
    //                 frappe.model.set_value(cdt, cdn, 'direct_manager_full_name', values.employee_name)
    //             })
    //     }
    //     else {
    //         frappe.model.set_value(cdt, cdn, 'direct_manager', '');
    //         frappe.model.set_value(cdt, cdn, 'direct_manager_full_name', '')
    //     }
    // }
});
