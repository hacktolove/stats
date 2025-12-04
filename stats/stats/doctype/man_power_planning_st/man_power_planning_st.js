// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Man Power Planning ST", {
    refresh(frm) {
        if (frm.doc.job_details.length > 0) {
            console.log("Refreshhh")
            frm.doc.job_details.forEach(job => {
                if (job.position_status == "Filled") {
                    console.log(job.name, "--------")
                    frm.set_df_property('job_details', 'read_only', 1, frm.docname, 'position_status', job.name)
                }
            });
        }
    },

	setup(frm) {
        frm.set_query("main_department", function (doc) {
			return {
				query: "stats.api.get_main_department",
			};
		});
        frm.set_query("job_family","job_details", function (doc,cdt,cdn){
                return {
                    query: "stats.api.get_main_job_family",
                }
		});
        frm.set_query("sub_job_family","job_details", function (doc,cdt,cdn){
                let row = locals[cdt][cdn]
                return {
                    filters: {
                        parent_job_family_st: row.job_family,
                        is_group: 0
                    }
                };
		});
        frm.set_query("main_job_department","job_details", function (doc,cdt,cdn){
            return {
                query: "stats.api.get_main_department",
            }
        });
        frm.set_query("sub_department","job_details", function (doc,cdt,cdn){
            let row = locals[cdt][cdn]
            if (row.main_job_department) {
                return {
                    query: "stats.api.get_descendant_departments",
                    filters: {
                        main_department: row.main_job_department,
                    }
                };
            }
                // return {
                //     filters: {
                //         parent_department: row.main_job_department,
                //         is_group: 0
                //     }
                // };
        })
    },

    supplier(frm) {
        if(frm.doc.supplier) {
            frappe.call({
				method: "stats.api.get_supplier_contact",
				args: {
					supplier: frm.doc.supplier
				}
			}).then(r => {
                if (r.message){
                    frm.set_value('contact_name', r.message)
                }
            })
        }
    }
});

frappe.ui.form.on("MP Jobs Details ST", {
    direct_manager(frm, cdt, cdn){
        let row = locals[cdt][cdn]
        if (row.direct_manager){
            frappe.db.get_value('Employee', row.direct_manager, 'employee_name')
                .then(r => {
                let employee_name = r.message.employee_name
                console.log(r.message.employee_name) // Open
                frappe.model.set_value(cdt, cdn, 'direct_manager_name', employee_name)
                })
        }
        else{
            frappe.model.set_value(cdt, cdn, 'direct_manager_name', '')
        }
    }
})