// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("High Potential ST", {
	onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department'])
            .then(r => {
                let values = r.message;
                console.log(values,"---")
                frm.set_value('created_by', values.employee_name)
                frm.set_value('department', values.department)
            })
        }  
    },

    setup(frm) {
        frm.set_query("main_department", function (doc) {
            return {
                query: "stats.api.get_main_department",
            };
        });
        frm.set_query("sub_department", function (doc) {
            if (frm.doc.main_department) {
                return {
                    filters: {
                        parent_department: frm.doc.main_department,
                        is_group: 0
                    }
                };
            }
        });
        // frm.set_query("employee_no", "high_performance_employee_details", function (doc, cdt, cdn) {
        //     let row = locals[cdt][cdn];
        //     return {
        //         query: "stats.stats.doctype.high_potential_st.high_potential_st.get_employee_list",
        //         filters: {
        //             no_of_years_for_retirement: frm.doc.no_of_years_for_retirement
        //         }
        //     };
        // });
    },

    fetch_employees(frm) {
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("high_performance_employee_details", "");
        frm.call("fetch_employees_from_employee_evaluation").then((r) => {
            let employee_list = r.message
            console.log(employee_list,"--------------")
            if (employee_list.length > 0) {
                employee_list.forEach((ele) => {
                    var d = frm.add_child("high_performance_employee_details");
                    frappe.model.set_value(d.doctype, d.name, "employee_no", ele.employee_no)
                    frappe.model.set_value(d.doctype, d.name, "employee_evaluation", ele.employee_evaluation)
                    frappe.model.set_value(d.doctype, d.name, "employee_evaluation_score", ele.employee_evaluation_score)
                })
                frm.refresh_field('high_performance_employee_details')
                frm.save()
            }
            else {
                frappe.msgprint(__('No Data Found'));
            }
        })
    }
});
