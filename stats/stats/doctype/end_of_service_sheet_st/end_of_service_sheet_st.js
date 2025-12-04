// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("End Of Service Sheet ST", {
	onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'employee_name')
                .then(r => {
                    let values = r.message;
                    frm.set_value('created_by', values.employee_name)
                })
        }
    },

    refresh(frm) {
        console.log(frm.doc,"-----------------")
        setTimeout(() => {
            $("button.grid-add-row").hide()
            $("button.grid-remove-rows").hide()
            $("button.grid-remove-all-rows").hide()   
        }, 100);
	},
    get_employee: function(frm){
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }
        frm.set_value("employee_details", "");
        frm.call("get_employee_details_for_end_of_service").then((r) => {
            let employee_list = r.message
            if (employee_list.length > 0) {
                employee_list.forEach((ele) => {
                    var d = frm.add_child("employee_details");
                    frappe.model.set_value(d.doctype, d.name, "employee_no", ele.employee_no)
                    frappe.model.set_value(d.doctype, d.name, "reference", ele.reference)
                    frappe.model.set_value(d.doctype, d.name, "total_salary", ele.total_salary)
                    frappe.model.set_value(d.doctype, d.name, "due_amount", ele.due_amount)
                    frappe.model.set_value(d.doctype, d.name, "eos_type", ele.eos_type)
                })
                frm.refresh_field('employee_details')
                frm.save()
            }
            else{
                frappe.toast(__("No resignation and retirement found."));
                frm.refresh_field('employee_details')
                frm.save()
            }
        })
    }
});
