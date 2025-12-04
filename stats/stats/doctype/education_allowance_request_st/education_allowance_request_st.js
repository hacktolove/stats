// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Education Allowance Request ST", {

    setup: function (frm) {
        frm.trigger("hide_grid_add_row");
    },

    onload: function(frm) {
        fetch_season(frm)
        fetch_terms_and_conditions(frm)
        set_season_type_options_in_child_table(frm)
        button_to_create_new_request_for_pending_amount(frm)
    },

    hide_grid_add_row: function (frm) {
        setTimeout(() => {
            frm.fields_dict.education_allowance_request_details.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);
    },

    onload_post_render(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['name','department','custom_sub_department','employee_name','grade','custom_section'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('employee_no', values.name)
                    frm.set_value('employee_name', values.employee_name)
                    frm.set_value('main_department', values.department)
                    frm.set_value('sub_department', values.custom_sub_department)
                    frm.set_value('section', values.custom_section)
                    frm.set_value('grade', values.grade)
                })
        }
    },

	employee_no(frm) {
        frm.set_value("education_allowance_request_details","")
        frm.set_value("employee_education_allowance_history","")
        // fetch employee child data from employee for current request
        if (frm.doc.season && frm.doc.educational_year) {
        frappe.call({
            method: "stats.stats.doctype.education_allowance_request_st.education_allowance_request_st.get_employee_dependants",
            args: {
                "employee": frm.doc.employee_no,
                "season": frm.doc.season,
                "educational_year": frm.doc.educational_year
            },
            callback: function(r) {
                if (r.message) {
                    let family_details = r.message
                    console.log(family_details,"=======")
                if (family_details) {
                    family_details.forEach((e) => {
                        var d = frm.add_child("education_allowance_request_details");
                        frappe.model.set_value(d.doctype, d.name, "child_name", e.name)
                        frappe.model.set_value(d.doctype, d.name, "relation", e.relation)
                        frappe.model.set_value(d.doctype, d.name, "date_of_birth", e.date_of_birth)
                        frappe.model.set_value(d.doctype, d.name, "age", e.age)
                        frappe.model.set_value(d.doctype, d.name, "season", e.season)
                        frappe.model.set_value(d.doctype, d.name, "child_reference", e.child_reference)
                        frappe.model.set_value(d.doctype, d.name, "ed_balance_amount",e.ed_balance_amount);
                        frappe.model.set_value(d.doctype, d.name, "ed_due_amount", e.ed_due_amount)
                        frappe.model.set_value(d.doctype, d.name, "id_number", e.id_number)
                    });
                    refresh_field("education_allowance_request_details");
                }


                //   set employee education allowance history   //

                frm.call("get_employee_dependants_history").then(
                    r => {
                        let history_details = r.message
                        console.log(history_details,"-----history_details")
                        if (history_details) {
                            history_details.forEach((e) => {
                                var d = frm.add_child("employee_education_allowance_history");
                                console.log("==============")
                                frappe.model.set_value(d.doctype, d.name, "child_name", e.child_name)
                                frappe.model.set_value(d.doctype, d.name, "relation", e.relation)
                                frappe.model.set_value(d.doctype, d.name, "date_of_birth", e.date_of_birth)
                                frappe.model.set_value(d.doctype, d.name, "age", e.age)
                                frappe.model.set_value(d.doctype, d.name, "season", e.season)
                                frappe.model.set_value(d.doctype, d.name, "child_reference", e.child_reference)
                                frappe.model.set_value(d.doctype, d.name, "ed_due_amount", e.ed_due_amount)
                                // frappe.model.set_value(d.doctype, d.name, "suggested_amount",e.suggested_amount);
                                frappe.model.set_value(d.doctype, d.name, "ed_balance_amount", e.ed_balance_amount);
                                frappe.model.set_value(d.doctype, d.name, "requested_amount",e.requested_amount);
                                frappe.model.set_value(d.doctype, d.name, "approved_amount", e.approved_amount);
                                frappe.model.set_value(d.doctype, d.name, "exceed_limit",e.exceed_limit);
                                frappe.model.set_value(d.doctype, d.name, "payment_attachment", e.payment_attachment);
                            });
                            refresh_field("employee_education_allowance_history");
                            set_season_type_options_in_child_table(frm)

                            frm.call("validate_per_child_per_release").then( r => {
                                console.log(r.message,"==")
                            })
                        }
                    }
                )
                }
            }
        })
        }
	},

    
    grade(frm) {
        // do not remove

    },

    creation_date(frm) {
        fetch_season(frm)
    },

    // after_workflow_action(frm) {
    //     frm.call("check_action_is_rejected").then(r => {
    //         // console.log(r.message)
    //         let is_rejected = r.message
    //         if (is_rejected) {
    //             frappe.prompt({
    //                 label: 'Reject Reason',
    //                 fieldname: 'reject_reason',
    //                 fieldtype: 'Small Text',
    //                 reqd: 1
    //             }, (values) => {
    //                 console.log(values.reject_reason);
    //                 frm.call("add_reject_reason", {reject_reason: values.reject_reason})
    //             })
    //         }
    //     })
    // }
});

// function set_grade_allowance_limit_value(frm) {
//     let grade = frm.doc.grade
//     if (grade){
//         frappe.db.get_value("Employee Grade",grade,"custom_education_allowance_amount").then(
//             r => {
//                 console.log(r.message,r.message.custom_education_allowance_amount)
//                 if (r.message.custom_education_allowance_amount){
//                     frm.set_value("allowance_limit",r.message.custom_education_allowance_amount)
//                 }
//             }
//         )
//     }  
// }

function fetch_season(frm) {
    let creation_date = frm.doc.creation_date
    if (frm.is_new()){
        // setTimeout(() => {
    frappe.db.get_list('Release Education Allowance ST', {
        fields: ['season', 'education_year','name'],
        filters: {
        activate: 'Yes',activate_from:['<=',creation_date],activate_till:['>=',creation_date]
        }
        }).then(records => {
        console.log(records,"===");
        // frappe.throw(__("No data"))
        if (records.length > 0) {
            console.log(records[0].education_year,records[0].name)
            frm.set_value("educational_year",records[0].education_year)
            frm.set_value("season",records[0].season)
            frm.set_value("release_reference",records[0].name)
        } else {
            frappe.throw(__("You cannot apply for Education Allowance because there is no any Active release to apply."))
        }
        })
        // }, 100);
    }
    

}

frappe.ui.form.on("Education Allowance Request Details ST", {
    requested_amount: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        frappe.call({
            method: "set_approved_amount",
            doc: frm.doc,
            args: {
                employee : frm.doc.employee_no,
                grade : frm.doc.grade,
                season : frm.doc.season,
                requested_amount : row.requested_amount,
                educational_year : frm.doc.educational_year,
                child_reference : row.child_reference,
                ed_balance_amount : row.ed_balance_amount
            },
            callback: function(r) {
                console.log(r.message,"---")
                if (r.message) {
                    frappe.model.set_value(cdt, cdn, "approved_amount", r.message.approved_amount);
                    frappe.model.set_value(cdt, cdn, "ed_due_amount", r.message.ed_due_amount);
                }

                // frm.call("validate_child_eligibility_based_on_requested_amount").then(
                //     r => {
                //         console.log(r.message)
                //     }
                // )
            }
        })
    },

    approved_amount: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        let due_amount = row.requested_amount - row.approved_amount
        if (due_amount > 0) {
            frappe.model.set_value(cdt, cdn, "ed_due_amount", due_amount);
        }
        // frm.call("validate_child_eligibility_based_on_requested_amount").then(
        //             r => {
        //                 console.log(r.message)
        //             }
        //         )
    }
})

let fetch_terms_and_conditions = function(frm) {
    frappe.db.get_single_value("Stats Settings ST","terms_and_conditions")
    .then(terms_and_conditions => {
        console.log(terms_and_conditions)
        frm.set_value("terms_and_conditions",terms_and_conditions)
    })
}

let set_season_type_options_in_child_table = function (frm) {
	if (frm.doc.educational_year) {
	frm.call("get_season_types").then(({message: types}) => {
		// set options for child table field --> Autocomplete field
		frm.fields_dict.education_allowance_request_details.grid.update_docfield_property(
		'season_type',
		'options',
		(types)
		);
        
        if (types && types.length==1){
            if (frm.doc.education_allowance_request_details && frm.doc.education_allowance_request_details.length>0){
                frm.doc.education_allowance_request_details.forEach((d) => {
                    if (!d.season_type){
                        frappe.model.set_value(d.doctype, d.name, "season_type", types[0])
                    }
                });
                refresh_field("education_allowance_request_details");
            }
        }
    })
	}
	
}

let button_to_create_new_request_for_pending_amount = function(frm) {
    if (frm.doc.docstatus == 1){
        frm.call("check_for_pending_amount").then(r => {
            let pending_amount = r.message.pending_amount
            console.log(pending_amount,"---pending_amount---")
            if (pending_amount && pending_amount > 0){
                frm.add_custom_button(__("Create New Request for Pending Amount"), function() {
                    frappe.call({
                        method: "stats.stats.doctype.education_allowance_request_st.education_allowance_request_st.create_new_request_for_pending_amount",
                        args: {
                            "source_name": frm.doc.name,
                            "target_doc": undefined,
                            "doctype": frm.doc.doctype
                        },
                        callback: function(r) {
                            if (r.message) {
                                let new_request = r.message
                                console.log(new_request,"---new_request---")
                                frappe.open_in_new_tab = true;
                                frappe.set_route("Form", "Education Allowance Request ST", new_request);
                            }
                        }
                    })
                });
            }
        })
    }
}