// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Permission Request ST", {
    onload(frm){console.log("Hello")},
	request_date(frm) {
        console.log("date")
        if (frm.doc.type_of_request === "Reconciliation Request" && frm.doc.request_date < frappe.datetime.get_today()) {
            frm.call("get_shortage_for_requested_date").then(r => {
                console.log(r.message,"===")
                if (r.message) {
                    frm.set_value("shortage_in_working_minutes", r.message.shortage_in_working_minutes);
                    frm.set_value("attendance_reference",r.message.attendance_reference)
                } else {
                    frm.set_value("shortage_in_working_minutes", 0);
                    frappe.throw(__("No shortage found for the requested date"));
                }
            });
        }
	}
});