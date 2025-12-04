// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Event ST", {

    onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
            .then(r => {
                let values = r.message;
                frm.set_value('employee', values.name)
            })
        }  
    },

    refresh(frm) {
        if (!frm.is_new() && (frm.doc.training_event_employee_details).length < 1) {
            frm.add_custom_button(__('Fetch Training Request'), () => fetch_training_request(frm));
        }
    },

	training_start_date(frm) {
        set_no_of_days(frm)
	},
    training_end_date(frm){
        set_no_of_days(frm)
    },
    ignore_holidays_in_no_of_days(frm){
        set_no_of_days(frm)
    }
});

let set_no_of_days = function (frm) {
    let start_date = frm.doc.training_start_date
    let end_date = frm.doc.training_end_date
    if (start_date && end_date) {
        let no_of_day = frappe.datetime.get_day_diff(end_date, start_date)
        if (frm.doc.ignore_holidays_in_no_of_days == 1){
            console.log("------------")
            frm.call("check_holiday_between_start_end_date").then(
                r => {
                    console.log(r.message)
                    holiday_count = r.message
                    frm.set_value("no_of_days", (no_of_day-holiday_count || 0)+1)
                }
            )
        }
        else{
            frm.set_value("no_of_days", (no_of_day || 0)+1)
        }
        frm.set_value("no_of_days", (no_of_day || 0)+1)
    }
}

let fetch_training_request = function(frm){
    if (frm.is_dirty() == true) {
        frappe.throw({
            message: __("Please save the form to proceed..."),
            indicator: "red",
        });
    }
    frm.set_value("training_event_employee_details", "");
    frm.call("fetch_training_request").then((r) => {
        let available_training_request_list = r.message
        if (available_training_request_list.length > 0){
            available_training_request_list.forEach((ele) => {
                var d = frm.add_child("training_event_employee_details");
                if (ele.name) {
                    frappe.model.set_value(d.doctype, d.name, "training_request_reference", ele.name)
                    frappe.model.set_value(d.doctype, d.name, "employee_no", ele.employee_no)
                }
            })
            frm.refresh_field('training_event_employee_details')
            frm.save()
        }
    })
}