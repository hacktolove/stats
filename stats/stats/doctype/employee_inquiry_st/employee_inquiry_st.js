// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Inquiry ST", {
	inquiry_type(frm) {
        frm.set_value("employee_inquiry_responsible_team_details", "");
        frm.call("get_employees_details_from_inquiry_type").then((r) => {
            if (r.message) {
               r.message.forEach((e) => {
                    var d = frm.add_child("employee_inquiry_responsible_team_details");
                    console.log(e, '--------e')
                    frappe.model.set_value(d.doctype, d.name, "employee", e.employee)
                    frappe.model.set_value(d.doctype, d.name, "employee_name", e.employee_name)
                    frappe.model.set_value(d.doctype, d.name, "email_id", e.email_id)
                    frappe.model.set_value(d.doctype, d.name, "mobile_no", e.mobile_no)
                });
                refresh_field("employee_inquiry_responsible_team_details");
            }
        })
	},
});
