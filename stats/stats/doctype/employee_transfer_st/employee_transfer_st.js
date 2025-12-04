// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Employee Transfer ST", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Managers Notes ST", {
	managers_notes_add(frm, cdt, cdn) {
        let logged_in_user = frappe.session.user
        frappe.db.get_value('User', logged_in_user, 'full_name')
        .then(r => {
        let values = r.message;
        console.log(values.full_name)
        frappe.model.set_value(cdt, cdn, "user_name", values.full_name)
        })
	},
});