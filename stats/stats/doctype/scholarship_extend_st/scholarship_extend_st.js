// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Scholarship Extend ST", {
	onload(frm) {
        if (frm.doc.scholarship_no) {
            frappe.db.get_value("Scholarship ST",{scholarship_no: frm.doc.scholarship_no},"permission_days")
            .then(r => {
                let plan_return_date = frappe.datetime.add_days(frm.doc.scholarship_end_date, r.message.permission_days)
                frm.set_value("permission_days",r.message.permission_days)
                frm.set_value("plan_return_date",plan_return_date)
            })
        }
	},  
});
