// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Offer ST", {
	setup(frm) {
		frm.set_query("main_department", function (doc) {
			return {
				query: "stats.api.get_main_department",
			};
		});
		frm.set_query("sub_department", function (doc) {
			if (frm.doc.main_department) {
				return {
                    query: "stats.api.get_descendant_departments",
                    filters: {
                        main_department: frm.doc.main_department,
                    }
                };
			}
		})

		if(frm.is_new() && frm.doc.job_application_reference){
			fill_education_qualification_and_work_history(frm)
		}
	},
	refresh: function (frm) {
		if (frm.doc.status == 'Accepted') {
			frm.set_df_property('date_of_birth', 'reqd', 1)
			frm.add_custom_button(
				__("Create Employee"),
				function () {
					frappe.model.open_mapped_doc({
						method: "stats.stats.doctype.job_offer_st.job_offer_st.make_employee",
						frm: frm,
					});
				});
		}
	},
	gender: function(frm) {
		if (frm.doc.gender) {
			frappe.db.get_value('Gender', frm.doc.gender, 'custom_is_male')
			.then(r => {
				console.log(r.message.custom_is_male)
				if (r.message.custom_is_male==1) {
					frm.set_df_property('personal_photo', 'reqd', 1)
				}
				else {
					frm.set_df_property('personal_photo', 'reqd', 0)
				}
			})
		}
	},
	job_application_reference: function(frm){
		// if(frm.is_new() && frm.doc.contract_type){
		// 	fill_salary_tables(frm)
		// }

		if(frm.is_new() && frm.doc.job_application_reference){
			fill_education_qualification_and_work_history(frm)
		}
	},

	basic_salary_amount: function(frm){
		frm.call("get_salary_details_from_grade");
		frm.call("validate_salary_basic_amount")
	},
	gosi_registration_date: function(frm){
		frm.call("set_gosi_type_and_percentage").then(() => {
			frm.refresh()
			frm.call("get_salary_details_from_grade");
		})
		
	},
	contract_type: function(frm) {
		// if(frm.is_new()){
		// 	fill_salary_tables(frm)
		// }
		// if (frm.is_new()) {
		// 	frm.set_value("earning", "");
		// 	frm.set_value("deduction", "");
		// 	if (frm.doc.contract_type) {
		// 		frappe.call({
		// 			method: "stats.stats.doctype.job_offer_st.job_offer_st.fetch_salary_tables_from_contract_type",
		// 			args: {
		// 				parent: frm.doc.contract_type,
		// 				parenttype: "Contract Type ST",
		// 			},
		// 			callback: function (r) {
		// 				if (r.message[0]) {
		// 					r.message[0].forEach((e) => {
		// 						frm.add_child("earning", e);
		// 					});
		// 					refresh_field("earning");
		// 				}
		// 				if (r.message[1]) {
		// 					r.message[1].forEach((d) => {
		// 						frm.add_child("deduction", d);
		// 					});
		// 					refresh_field("deduction");
		// 				}
		// 			},
		// 		});
		// 	}
		// }
		
	}
});

// frappe.ui.form.on("Job Offer Details ST", {
// 	offer_term: function (frm, cdt, cdn) {
// 		let row = locals[cdt][cdn]
// 		frappe.db.get_value('Offer Term', row.offer_term, 'custom_is_monthly_salary_component')
// 		.then(r => {
// 			if(r.message.custom_is_monthly_salary_component == 1){
// 				frm.call({
// 					doc: frm.doc,
// 					method: "get_salary_amount_from_man_power_planning",
// 					freeze: true,
// 					callback: (r) => {
// 						if (r.message) {
// 							console.log(r.message,'--------msg')
// 							frappe.model.set_value(cdt, cdn, 'value', r.message)
// 						}
// 					}
// 				})
// 			}
// 		})
// 	},
// 	value: function (frm, cdt, cdn) {
// 		let row = locals[cdt][cdn]
// 		if (row.offer_term) {
// 			frappe.db.get_value('Offer Term', row.offer_term, 'custom_is_monthly_salary_component')
// 				.then(r => {
// 					if(r.message.custom_is_monthly_salary_component == 1){
// 						if(frm.is_new() && frm.doc.contract_type){
// 							fill_salary_tables(frm)
// 						}
// 					} 
// 				})
// 		}
// 	}
// })

let fill_salary_tables = function(frm) {
	frm.call("fill_salary_tables");
	// frm.save()
}

let fill_education_qualification_and_work_history = function(frm){
	frm.call("fill_education_qualification_and_work_history")
}