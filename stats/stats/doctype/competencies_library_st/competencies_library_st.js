// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Competencies Library ST", {
	refresh(frm) {

	},
});

frappe.ui.form.on("Competencies Library Details ST", {
    select_elements(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log("Clicked")
        let dialog = undefined
        const dialog_field = []
        dialog_field.push({
            label: 'Elements',
            fieldname: 'elements',
            fieldtype: 'Table MultiSelect',
            options: 'Competencies Elements Table ST',
            reqd: 1,
            })
        
        dialog = new frappe.ui.Dialog({
                title: __("Select Elements for Competency"),
                fields: dialog_field,
                primary_action_label: 'Add',
                primary_action: function (values) {
                    console.log(values)
                    frappe.call({
                    method: "stats.stats.doctype.competencies_library_st.competencies_library_st.set_elements_in_childtable",
                    args: {
                        element: values.elements
                    },
                    callback: function (r) {
                        console.log(r,"r")
                        if (r.message) {
                            frappe.model.set_value(cdt, cdn, "elements", r.message);
                        }
                    }
                });
                dialog.hide();                    
                }
            })
            dialog.show()
    }
});