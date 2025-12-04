// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Certificate of Appreciation ST", {
    onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
            .then(r => {
                let values = r.message;
                frm.set_value('employee', values.name)
            })
        }  
    },
    setup(frm){
        frm.set_query("employee_no","main_department_invitation", function (doc,cdt,cdn){
            return {
                query: "stats.stats.doctype.certificate_of_appreciation_st.certificate_of_appreciation_st.get_main_department_manager",
            }
        });
    }
});
