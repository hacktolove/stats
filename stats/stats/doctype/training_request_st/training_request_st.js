// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Request ST", {
    setup(frm) {
        frm.set_query("training_event",function (doc){
            return {
                query: "stats.stats.doctype.training_request_st.training_request_st.get_training_events",
                filters : {
                    employee_no : frm.doc.employee_no,
                    request_date : frm.doc.date
                }
            };
        });
    },
});
