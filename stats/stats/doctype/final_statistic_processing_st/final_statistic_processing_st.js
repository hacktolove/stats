// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Final Statistic Processing ST", {
	onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'employee_name')
            .then(r => {
                let values = r.message;
                frm.set_value('created_by', values.employee_name)
            })
        }  
    },
    fetch_statistic_request: function(frm){
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }
    
        frm.call("fetch_department_vise_statistic_request").then((r) => {
            if (r.message) {
                console.log(r.message, "r.message")
            }
        })
    }
});
