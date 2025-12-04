// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Man Power Plan Change Request ST", {
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
		});

        frm.set_query("job_no", function (doc){
            if (frm.doc.man_power_planning_reference) {
                return {
                        query: "stats.stats.doctype.man_power_plan_change_request_st.man_power_plan_change_request_st.get_job_no",
                        filters: {
                            parent : frm.doc.man_power_planning_reference
                        } 
                };       
            }
		});

        frm.set_query("new_job_no", function (doc){
            if (frm.doc.man_power_planning_reference) {
                return {
                        query: "stats.stats.doctype.man_power_plan_change_request_st.man_power_plan_change_request_st.get_job_no",
                        filters: {
                            parent : frm.doc.man_power_planning_reference
                        } 
                };       
            }
		});

        // update previous
        frm.set_query("main_department_cp", function (doc) {
			return {
				query: "stats.api.get_main_department",
			};
		});
		frm.set_query("sub_department_cp", function (doc){
            if (frm.doc.main_department_cp) {
                return {
                    filters: {
                        parent_department: frm.doc.main_department_cp,
                        is_group: 0
                    }
                };       
            }
		});

        // create new job 
        frm.set_query("main_department_nj", function (doc) {
			return {
				query: "stats.api.get_main_department",
			};
		});
		frm.set_query("sub_department_nj", function (doc){
            if (frm.doc.main_department_nj) {
                return {
                    filters: {
                        parent_department: frm.doc.main_department_nj,
                        is_group: 0
                    }
                };       
            }
		})
    },
    job_no(frm){
        if(frm.doc.job_no){
            frappe.call({
				method: "stats.stats.doctype.opening_job_st.opening_job_st.get_job_deatils",
				args: {
					job_title: frm.doc.job_no
				}
			}).then(r => {
                if (r.message){
                    frm.set_value({
                        salary: r.message.salary,
                        grade: r.message.grade,
                        designation: r.message.designation,
                        pre_main_department: r.message.main_job_department,
                        pre_sub_department: r.message.sub_department, 
                        section: r.message.section,
                        employee_unit: r.message.employee_unit 
                    })
                }
            })
        }
    }
});
