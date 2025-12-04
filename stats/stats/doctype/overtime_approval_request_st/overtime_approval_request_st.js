// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Overtime Approval Request ST", {
	onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'employee_name')
            .then(r => {
                let values = r.message;
                frm.set_value('created_by', values.employee_name)
            })
        }  
    }
});

frappe.ui.form.on("Overtime Approval Employee Details ST", {
    deduct_vacation_and_absent_days(frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        frm.call("deduct_vacation_and_absent_based_on_checkbox").then(
            r => {
                console.log(r.message,"==")
                if (r.message) {
                    frappe.model.set_value(cdt, cdn, "no_of_vacation", r.message.no_of_vacation)
                    frappe.model.set_value(cdt, cdn, "no_of_absent", r.message.no_of_absent)
                    frappe.model.set_value(cdt, cdn, "expected_approved_days", r.message.expected_approved_days)
                    frappe.model.set_value(cdt, cdn, "approved_days", r.message.expected_approved_days)
                }
            }
        )
    }
})
