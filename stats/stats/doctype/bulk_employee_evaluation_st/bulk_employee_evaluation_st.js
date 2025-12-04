// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Employee Evaluation ST", {
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
        })
    },

    onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('created_by', values.employee_name)
            })
        }
    },

    refresh(frm) {
        let reference_found = false
        let bulk_evaluation_details = frm.doc.bulk_evaluation_details
        if (bulk_evaluation_details.length >0) {
            for (row of frm.doc.bulk_evaluation_details) {
                if (row.evaluation_reference) {
                    reference_found = true
                    break
                }
            }
        }
        if (reference_found == true) {
            frm.set_df_property('create_evaluation', 'hidden', 1);
        }
    },

    evaluation_type(frm) {
        let previous_year_start_date = frappe.datetime.add_months(frappe.datetime.year_start(),-12)
        let previous_year_end_date = frappe.datetime.add_days(frappe.datetime.year_start(),-1)

        if (frm.doc.evaluation_type == "Yearly") {
            console.log("Yearly ")
            frm.set_value("from_date", previous_year_start_date)
            frm.set_value("to_date", previous_year_end_date)
        }

        else if (frm.doc.evaluation_type == "Half Yearly") {
            
            let month = frappe.datetime.str_to_obj(frm.doc.creation_date).getMonth() + 1
            console.log(month,"month")
            if (month < 7) {
                let previous_half_end =  frappe.datetime.add_days(frappe.datetime.year_start(),-1)
                let previous_half_start = frappe.datetime.add_months(frappe.datetime.add_days(frappe.datetime.year_start()), -6)
                console.log(previous_half_start, previous_half_end, "---7 to 12")
                frm.set_value("from_date", previous_half_start)
                frm.set_value("to_date", previous_half_end)
            }

            if (month >= 7) {
                let previous_half_start = frappe.datetime.year_start()
                let previous_half_end = frappe.datetime.add_days(frappe.datetime.add_months(frappe.datetime.year_start(), 6),-1)
                console.log(previous_half_start, previous_half_end, "---1 to 6")
                frm.set_value("from_date", previous_half_start)
                frm.set_value("to_date", previous_half_end)
            }
        }
    },

    fetch_employee(frm){
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("bulk_evaluation_details", "");
        frm.call("get_employees").then((r) => {
            console.log(r, "r")
            let employee_list = r.message

            if (employee_list.length > 0) {
                employee_list.forEach((ele) => {
                    var d = frm.add_child("bulk_evaluation_details");
                    frappe.model.set_value(d.doctype, d.name, "employee_no", ele.name)
                })
                frm.refresh_field('bulk_evaluation_details')
                frm.save()
            }
        })
    },

    create_evaluation(frm){
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        // frm.set_value("bulk_evaluation_details", "");
        frm.call("create_employee_evaluation").then((r) => {
            console.log(r, "r")
            let evaluation_list = r.message
            let bulk_evaluation_details = frm.doc.bulk_evaluation_details
            if (bulk_evaluation_details.length) {
                bulk_evaluation_details.forEach((ele) => {
                    evaluation_list.forEach((evaluation) => {
                        if (ele.employee_no == evaluation.employee_no) {
                            frappe.model.set_value(ele.doctype, ele.name, "evaluation_reference", evaluation.evaluation_reference)
                            frappe.model.set_value(ele.doctype, ele.name, "workflow_status", evaluation.evaluation_workflow_state)

                        }
                    })
                })
            }
            frm.refresh_field('bulk_evaluation_details')
            frm.save()
        })
    }
});
