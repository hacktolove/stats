// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Education Allowance Sheet ST", {
    onload(frm) {
        frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department', 'custom_sub_department'])
            .then(r => {
                let values = r.message;
                frm.set_value('created_by', values.employee_name)
                frm.set_value('main_department', values.department)
                frm.set_value('sub_department', values.custom_sub_department)
            })
    },

    fetch_approved_request(frm) {

        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("education_allowance_sheet_details","")
        frm.call("fetch_education_allowance_requests").then(
            r => {
                console.log(r.message,"--message")
                let request_details = r.message
                if (request_details) {
                    request_details.forEach((e) => {
                        var d = frm.add_child("education_allowance_sheet_details");
                        frappe.model.set_value(d.doctype, d.name, "education_allowance_request_reference", e.name)
                        frappe.model.set_value(d.doctype, d.name, "employee_no", e.employee_no)
                        frappe.model.set_value(d.doctype, d.name, "approved_amount", e.approved_amount)
                    });
                    refresh_field("education_allowance_sheet_details");
                    frm.save()
                }
            }
        )
    }
});
