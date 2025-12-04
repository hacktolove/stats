// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Competencies Elements ST", {
    onload(frm) {
        setTimeout(() => {
            frm.fields_dict.competencies_elements_details.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.competencies_elements_details.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);


        if (frm.is_new()) {
            frappe.db.get_value("Stats Settings ST", "Stats Settings ST", ["level_1", "level_2", "level_3"])
                .then(r => {
                    if (r.message.level_1 && r.message.level_2 && r.message.level_3) {
                        let values = [r.message.level_1, r.message.level_2, r.message.level_3];
                        console.log(values, "======")
                        values.forEach(element => {
                            var d = frm.add_child("competencies_elements_details");
                            frappe.model.set_value(d.doctype, d.name, "level", element)
                        });
                        frm.refresh_field('competencies_elements_details')
                    } else {
                        frappe.throw(__("Please set Different Levels in Stats Settings ST --> Allowance Tab"))
                    }
                })
        }

        
    },
});
