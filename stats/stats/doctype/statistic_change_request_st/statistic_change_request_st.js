// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Statistic Change Request ST", {
    onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'employee_name')
            .then(r => {
                let values = r.message;
                frm.set_value('created_by', values.employee_name)
            })
        }  
    },
	setup(frm) {
        frm.set_query("statistic_request_reference", function (doc) {
            return {
                query: "stats.stats.doctype.statistic_change_request_st.statistic_change_request_st.get_final_approved_statistic_request",
            };
        })
	},
});
