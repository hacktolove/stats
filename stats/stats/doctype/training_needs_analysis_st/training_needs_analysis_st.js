// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Needs Analysis ST", {
	onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
            .then(r => {
                let values = r.message;
                frm.set_value('employee', values.name)
            })
        }  
    },

    setup(frm) {
        frm.set_query("main_department", function (doc) {
            console.log("0101 نائب الرئيس للعمليات - GS")
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
            } else {
                return {
                    filters: {
                        is_group: 0
                    }
                };
            }
        })
    },

    refresh(frm) {
        if (!frm.is_new() && (frm.doc.training_needs_analysis_employee_details).length < 1) {
            frm.add_custom_button(__('Training Request'), () => fetch_training_request(frm), __("Fetch"));
        }
        if (!frm.is_new() && (frm.doc.training_needs_analysis_employee_details).length < 1) {
            frm.add_custom_button(__('Evaluation Recommendation'), () => fetch_evaluation_recommendation(frm), __("Fetch"));
        }     
    }
});

frappe.ui.form.on("Training Needs Analysis Employee Details ST", {
	check_evaluation(frm,cdt,cdn) {
        let row=locals[cdt][cdn]
        if (row) {
            frappe.route_options = {
                employee_no:row.employee_no,
                order_by: "creation desc",
            };
            frappe.set_route("List", "Training Evaluation ST");        
        }
    },
})
let fetch_training_request = function(frm){
    if (frm.is_dirty() == true) {
        frappe.throw({
            message: __("Please save the form to proceed..."),
            indicator: "red",
        });
    }
    frm.call("fetch_training_request").then((r) => {
        let available_training_request_list = r.message
        if (available_training_request_list.length > 0){
            available_training_request_list.forEach((ele) => {
                var d = frm.add_child("training_needs_analysis_employee_details");
                frappe.model.set_value(d.doctype, d.name, "training_request_reference", ele.name)
            })
            frm.refresh_field('training_needs_analysis_employee_details')
            frm.save()
        }
    })
}

let fetch_evaluation_recommendation = function(frm) {
    console.log("Evaluation Recommendation")
}