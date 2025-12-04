// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Contract ST", {

	setup(frm) {
        frm.set_query("main_department", function (doc) {
			return {
				query: "stats.api.get_main_department",
			};
		});
		frm.set_query("sub_department", function (doc){
            if (frm.doc.main_department) {
                return {
                    filters: {
                        parent_department: frm.doc.main_department,
                        is_group: 0
                    }
                };       
            }
		})
    },

	job_offer_reference: function (frm) {
		// frm.set_value("earning", "");
        // frm.set_value("deduction", "");

		frm.set_value("earnings_details", "");
		frm.set_value("deduction_details", "");

		if (frm.doc.job_offer_reference) {
			frappe.call({
				method: "stats.stats.doctype.employee_contract_st.employee_contract_st.get_salary_details",
				args: {
					parent: frm.doc.job_offer_reference,
					parenttype: "Job Offer ST",
				},
				callback: function (r) {
					console.log(r.message, "===r.message")
					if (r.message[0]) {
						r.message[0].forEach((e) => {
							// frm.add_child("earning", e);
							frm.add_child("earnings_details", e);
						});
						refresh_field("earnings_details");
					}
                    if (r.message[1]) {
						r.message[1].forEach((d) => {
							// frm.add_child("deduction", d);
							frm.add_child("deduction_details", d);
						});
						refresh_field("deduction_details");
					}
				},
			});

			frappe.db.get_value('Employee', { custom_job_offer_reference: frm.doc.job_offer_reference }, 'name')
				.then(r => {
					let employee = r.message;
					console.log(employee.name)
					frm.set_value("employee_no", employee.name);
				})
		}
	},
    contract_start_date: function(frm){
        if(frm.doc.contract_start_date){
            let trial_period = frappe.datetime.add_months(frm.doc.contract_start_date, 3)
			let contract_end_date = frappe.datetime.add_months(frm.doc.contract_start_date, 12)
			contract_end_date = frappe.datetime.add_days(contract_end_date, -1)
            frm.set_value('test_period_end_date', trial_period)
			frm.set_value('contract_end_date', contract_end_date)

        }
        else{
            frm.set_value('test_period_end_date', '')
        }
    },
    test_period_renewed: function(frm){
        if(frm.doc.test_period_renewed == "Yes"){
			frm.call("validate_trial_period")
        }
        else{
            frm.set_value('end_of_new_test_period', '')
        }
    }
});
