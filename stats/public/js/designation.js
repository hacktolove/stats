frappe.ui.form.on("Designation", {

    setup (frm) {
        frm.trigger("hide_grid_add_row");
    },

    hide_grid_add_row: function (frm) {
        setTimeout(() => {
            frm.fields_dict.custom_basic_competencies.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.custom_basic_competencies.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.custom_technical_competencies.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.custom_technical_competencies.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.custom_leadership.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.custom_leadership.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);
    },
    custom_sub_job_family (frm){
        frm.set_value("custom_basic_competencies","");
        frm.set_value("custom_technical_competencies","");
        frm.set_value("custom_leadership","");
        if (frm.doc.custom_sub_job_family) {
            frappe.call({
				method: "stats.api.get_competencies_details_and_set_in_child_tables",
				args: {
                    // doctype: frm.doc.doctype,
					// docname: frm.doc.name,
                    sub_job_family: frm.doc.custom_sub_job_family
				},
				callback: function (data) {
					console.log(data,"data")
                    let basic_competencies_details = data.message.basic_competencies_details
                    let technical_competencies_details = data.message.technical_competencies_details
                    let leadership_competencies_details = data.message.leadership_competencies_details
					if (basic_competencies_details.length > 0) {
                        basic_competencies_details.forEach((item) => {
                            let row = frm.add_child("custom_basic_competencies");
                            row.competencies_name = item.competencies_name;
                            row.definition = item.definition;
                            row.elements = item.elements;
                            frm.refresh_field("custom_basic_competencies");
                        });
					}
                    if (technical_competencies_details.length > 0) {
                        technical_competencies_details.forEach((item) => {
                            let row = frm.add_child("custom_technical_competencies");
                            row.competencies_name = item.competencies_name;
                            row.definition = item.definition;
                            row.elements = item.elements;
                            frm.refresh_field("custom_technical_competencies");
                        });
                    }
                    if (leadership_competencies_details.length > 0) {
                        leadership_competencies_details.forEach((item) => {
                            let row = frm.add_child("custom_leadership");
                            row.competencies_name = item.competencies_name;
                            row.definition = item.definition;
                            row.elements = item.elements;
                            frm.refresh_field("custom_leadership");
                        });
                    }
				}
			});
        }
    }
})

frappe.ui.form.on("Competencies Details ST", {
    weight(frm,cdt,cdn){
        // set_degree_based_on_weight(frm,cdt,cdn)
    },

    // degree_out_of_5(frm,cdt,cdn){
    //     set_degree_based_on_weight(frm,cdt,cdn)
    // },

    level(frm,cdt,cdn){
        let row = locals[cdt][cdn]
        frappe.call({
        method: "stats.api.fetch_definition_based_on_elements",
        args: {
            level: row.level,
            elements: row.elements
        },
        callback: function(r) {
            if (r.message) {
                frappe.model.set_value(cdt,cdn,"elements_and_definitions",r.message)
            }
        }
    });
    }
})

let set_degree_based_on_weight = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    if (row.weight && row.degree_out_of_5) {
        let degree_based_on_weight = (row.weight * row.degree_out_of_5) / 100
        frappe.model.set_value(cdt, cdn, "degree_based_on_weight", degree_based_on_weight)
    }
}