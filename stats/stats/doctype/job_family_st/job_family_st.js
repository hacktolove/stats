frappe.ui.form.on("Job Family ST", {
	onload: function (frm) {
		set_competencies_as_options_in_child_table(frm)
		frm.set_query("parent_job_family_st", function () {
			return { filters: [["Job Family ST", "is_group", "=", 1]] };
		});
	},
	refresh: function (frm) {
		// read-only for root department
		set_competencies_as_options_in_child_table(frm)
		if (!frm.doc.parent_job_family_st && !frm.is_new()) {
			frm.set_read_only();
			frm.set_intro(__("This is a root job family and cannot be edited."));
		}
	},
	validate: function (frm) {
		if (frm.doc.name == "All Job Families") {
			frappe.throw(__("You cannot edit main root node."));
		}
	},
	competencies_library: function (frm) {
		set_competencies_as_options_in_child_table(frm)
	}
});

let set_competencies_as_options_in_child_table = function (frm) {
	if (frm.doc.competencies_library) {
	frm.call("get_competencies_name").then(({message: competencies}) => {
		// set options for child table field --> Autocomplete field
		frm.fields_dict.competencies_library_details_table.grid.update_docfield_property(
		'competencies_name',
		'options',
		(competencies)
		);
    })
	}
	
}

frappe.ui.form.on("Competencies Library Details Table ST", {
	competencies_name: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.competencies_name) {
			frappe.call({
				method: "stats.stats.doctype.job_family_st.job_family_st.get_competencies_details",
				args: {
					competencies_library: frm.doc.competencies_library,
					competencies_name: row.competencies_name
				},
				callback: function (data) {
					console.log(data,"data")
					if (data.message) {
						// row.description = data.message.description;
						frappe.model.set_value(cdt, cdn, "category", data.message[0].category);
						frappe.model.set_value(cdt, cdn, "elements", data.message[0].elements);
						frappe.model.set_value(cdt, cdn, "definition", data.message[0].definition);
					}
				}
			});
		}
	}
});