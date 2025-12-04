// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Salary Document Request ST", {
	employee_no(frm) {
        frm.set_value("salary_details","")
        frm.call("get_salary_details").then(
            r => {
                let salary_details = r.message
                let total_salary = 0
                if (salary_details) {
                    salary_details.forEach((e) => {
                        var d = frm.add_child("salary_details");
                        frappe.model.set_value(d.doctype, d.name, "earning_name", e.salary_component)
                        frappe.model.set_value(d.doctype, d.name, "amount", e.amount)
                        total_salary = total_salary + e.amount

                    });
                    refresh_field("salary_details");
                }
                frm.set_value("total_salary",total_salary)
            }
        )

	},

    designation(frm) {
        setTimeout(() => {
            frappe.db.get_value('Designation', frm.doc.designation, 'custom_designation_in_english')
                .then(r => {
                frm.set_value("designation_in_english",r.message.custom_designation_in_english)
            })
        }, 500);
    }
});
