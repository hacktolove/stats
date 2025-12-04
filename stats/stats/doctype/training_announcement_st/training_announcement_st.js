// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Announcement ST", {
	onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
            .then(r => {
                let values = r.message;
                frm.set_value('employee', values.name)
            })
        }  
    },
});

frappe.ui.form.on("Training Announcement Details ST", {
	training_announcement_details_add(frm, cdt, cdn) {
         if(frm.doc.apply_start_date && frm.doc.apply_end_date){
            frappe.model.set_value(cdt, cdn, 'apply_start_date', frm.doc.apply_start_date);
            frappe.model.set_value(cdt, cdn, 'apply_end_date', frm.doc.apply_end_date);
         }
    },
});