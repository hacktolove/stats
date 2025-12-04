// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchasing Committee ST", {
	onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'employee_name')
                .then(r => {
                    let values = r.message;
                    frm.set_value('created_by', values.employee_name)
                })
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'department')
            .then(r => {
                let values = r.message;
                frm.set_value('main_department', values.department)
            })
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'custom_sub_department')
            .then(r => {
                let values = r.message;
                frm.set_value('sub_department', values.custom_sub_department)
            })
        }
    },
});
