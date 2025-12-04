// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Opening Job ST", {
	setup(frm) {
        frm.set_query("job_title", function (doc) {
            console.log("hellooo")
			return {
				query: "stats.stats.doctype.opening_job_st.opening_job_st.get_job_no",
			};
		});

        frm.set_query("main_department", function (doc) {
			return {
				query: "stats.api.get_main_department",
			};
		});

		frm.set_query("sub_department", function (doc){
            if (frm.doc.main_department) {
                return {
                    query: "stats.api.get_descendant_departments",
                    filters: {
                        main_department: frm.doc.main_department,
                    }
                };      
            }
		})
    },

    job_title(frm){
        if(frm.doc.job_title){
            frappe.call({
				method: "stats.stats.doctype.opening_job_st.opening_job_st.get_job_deatils",
				args: {
					job_title: frm.doc.job_title
				}
			}).then(r => {
                console.log(r.message, '---r.message')
                if (r.message){
                    frm.set_value({
                        designation: r.message.designation,
                        main_department: r.message.main_job_department,
                        sub_department: r.message.sub_department,
                        grade: r.message.grade,
                        section: r.message.section,
                        branch : r.message.branch,
                        employment_type: r.message.employment_type,
                        contract_type: r.message.contract_type
                    })
                }
            })
        }
    }
});
