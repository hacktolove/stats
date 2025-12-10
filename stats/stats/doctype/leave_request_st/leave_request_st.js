// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Request ST", {
	setup(frm) {
        frm.toggle_display(["custom_relative"]  , false);

        frm.set_query("leave_type", function() {
            return {
                query: "stats.stats.doctype.leave_request_st.leave_request_st.get_leave_type",
                filters: {
                    "gender" : frm.doc.gender,
                    "religion": frm.doc.religion,
                    "contract_type": frm.doc.contract_type,
                    "marital_status": frm.doc.marital_status,
                    "employee": frm.doc.employee_no,
                    "leave_category": frm.doc.leave_category
                }
            }
        })
	},
    onload(frm){

        make_leave_type_readonly_for_civil_contract_employees(frm)
        // workflow_progressbar(frm)
        if (frm.doc.leave_request_reference) {
            frm.set_df_property("leave_type","read_only",1)
        }
        frm.set_query("deputy_employee", function () {
                return {
                    query: "stats.api.get_deputy_employee_list",
                    filters: {
                        employee: frm.doc.employee_no
                    }
                };
        });
    },

    refresh(frm) {
        make_leave_type_readonly_for_civil_contract_employees(frm)
        make_attachment_mandatory_based_on_condition(frm)
        // workflow_progressbar(frm)
        frappe.db.get_value('Stats Settings ST','Stats Settings ST', ['new_baby_leave_type','baby_extended_leave_type','baby_health_leave_type'])
            .then(r => {
            let new_baby_leave_type = r.message.new_baby_leave_type
            let baby_extended_leave_type = r.message.baby_extended_leave_type
            let baby_health_leave_type = r.message.baby_health_leave_type

            frappe.db.get_list('Leave Request ST', {
                            fields: ['name'],
                            filters: {leave_request_reference: frm.doc.name}
                }).then(records => {
                    if (records.length == 0) {
                        if (frm.doc.docstatus == 1 && frm.doc.leave_type == new_baby_leave_type){
                            frm.add_custom_button(__("New Baby Extended Vacation"), () => create_leave_request_for_baby_extended_vacation(frm, "Extended"), __("Create"))
                            frm.add_custom_button(__("New Baby Medical Vacation"), () => create_leave_request_for_baby_medical_vacation(frm, "Medical"), __("Create"))
                        }
                    }
                })
            if (frm.doc.docstatus == 1 && frm.doc.leave_type == baby_health_leave_type){
                frm.add_custom_button(__("New Baby Extended Vacation"), () => create_leave_request_for_baby_extended_vacation_from_medical(frm, "Extended"), __("Create"))
            }
        })
        if (frm.doc.docstatus === 0) {
			frm.trigger("make_dashboard");
		}
    },

    make_dashboard: function (frm) {
		let leave_details;
		let lwps;

        if (frm.doc.employee_no) {
            frappe.db.get_value('Stats Settings ST', 'Stats Settings ST', ['sick_leave_type_1_direct', 'sick_leave_type_2_direct', 'sick_leave_type_3_direct',
                "sick_leave_type_1_civil","sick_leave_type_2_civil","sick_leave_type_3_civil","sick_leave_type_4_civil","fatal_sick_leave_type_1",
                "fatal_sick_leave_type_2","fatal_sick_leave_type_3","fatal_sick_leave_type_4"])
                .then(r => {
                    let values = r.message;
                    console.log(values)
                    let leave_type_list = [values.sick_leave_type_1_direct, values.sick_leave_type_2_direct, values.sick_leave_type_3_direct, values.sick_leave_type_1_civil, values.sick_leave_type_2_civil,
                    values.sick_leave_type_3_civil, values.sick_leave_type_4_civil, values.fatal_sick_leave_type_1, values.fatal_sick_leave_type_2,
                    values.fatal_sick_leave_type_3, values.fatal_sick_leave_type_4]
                    console.log(leave_type_list, "---")
                    if (leave_type_list.includes(frm.doc.leave_type)) {
                        frappe.call({
                            method: "stats.stats.doctype.leave_request_st.leave_request_st.get_leave_details",
                            async: false,
                            args: {
                                employee: frm.doc.employee_no,
                                date: frm.doc.from_date || frappe.datetime.nowdate(),
                                leave_type: frm.doc.leave_type
                            },
                            callback: function (r) {
                                console.log("IN FUNCTION", r.message)
                                if (!r.exc && r.message["leave_allocation"]) {
                                    console.log(r.message["leave_allocation"], "=====")
                                    leave_details = r.message;
                                }
                            },
                        });

                        $("div").remove(".form-dashboard-section.custom");

                        frm.dashboard.add_section(
                            frappe.render_template("leave_request_st_dashboard", {
                                data: leave_details,
                            }),
                            __("Allocated Leaves"),
                        );

                        frm.dashboard.show();
                    }
                    else {
                         frm.dashboard.hide();
                    }
        })
		}
	},

    leave_type: function (frm) {
        frm.trigger("make_dashboard");
        make_attachment_mandatory_based_on_condition(frm)
        console.info("HEEEEEEEEEEEERRRRRRRREEEEEEEEEEEEEEE", frm.doc.leave_type)
        frm.toggle_display(["custom_relative"]  , true);

        frappe.db.get_value("Leave Type", frm.doc.leave_type, "custom_require_relative")
        .then(value => {
            if(value.message.custom_require_relative == 1){
                frm.toggle_display(["custom_relative"]  , true);
                frm.set_df_property("custom_relative", "reqd", 1)
            }
            else{
                frm.toggle_display(["custom_relative"]  , false);
                frm.set_df_property("custom_relative", "reqd", 0)
            }
            console.info("VALUE", value.message.custom_require_relative)
        }).catch(err => {
            console.error("ERROR", err)
        })
    },
    from_date: function (frm) {
        frm.trigger("make_dashboard");
    },

    to_date: function (frm) {
        frm.trigger("make_dashboard");
    },

    employee: function (frm) {
        make_leave_type_readonly_for_civil_contract_employees(frm)
    },

    leave_category: function (frm) {
        make_attachment_mandatory_based_on_condition(frm)
        make_leave_type_readonly_for_civil_contract_employees(frm)
    }
});

function create_leave_request_for_baby_medical_vacation(frm) {
    console.log("Medical Vacation");
    frappe.model.open_mapped_doc({
        method: "stats.stats.doctype.leave_request_st.leave_request_st.open_leave_request_for_baby_medical_vacation",
        frm: frm
    });
}

function create_leave_request_for_baby_extended_vacation(frm) {
    frappe.model.open_mapped_doc({
        method: "stats.stats.doctype.leave_request_st.leave_request_st.open_leave_request_for_baby_extended_vacation",
        frm: frm
    });
}

function create_leave_request_for_baby_extended_vacation_from_medical(frm) {
    frappe.model.open_mapped_doc({
        method: "stats.stats.doctype.leave_request_st.leave_request_st.create_leave_request_for_baby_extended_vacation_from_medical",
        frm: frm
    });
}

function make_leave_type_readonly_for_civil_contract_employees(frm) {
    let contract_type = frm.doc.contract_type
    let leave_category = frm.doc.leave_category
    
    if (__(contract_type) == __("Civil") && __(leave_category) == __("Sick")) {
        
        frappe.db.get_single_value('Stats Settings ST', 'leave_approver_role')
            .then(leave_approver_role => {
            // console.log(leave_approver_role,"===================");
            session_user_roles = frappe.user_roles
            // console.log(session_user_roles,"user roles")
            if (leave_approver_role) {
                
                if (!session_user_roles.includes(leave_approver_role)) {
                    console.log("NO LEAVE APPROVER")
                    frm.set_df_property("leave_type", "read_only", 1)
                    frm.set_df_property("leave_type", "reqd", 0)
                }
            }
        })
    } else {
        frm.set_df_property("leave_type", "read_only", 0)
        frm.set_df_property("leave_type", "reqd", 1)
    }
}

function workflow_progressbar(frm) {
    // console.log("---------workflow_progressbar-----------", frm.fields_dict["progress_bar"], "===", frm.doc.__onload )
    if (
        frm.fields_dict["progress_bar"] &&
        frm.is_new() == undefined &&
        frm.doc.__onload && "workflow_progressbar_html" in frm.doc.__onload
    ) {
        console.log("Inside IFFF")
        frm.set_df_property('progress_bar', 'options', frm.doc.__onload.workflow_progressbar_html)
        frm.refresh_field('progress_bar')
    }else{
        console.log("Inside ELSEEEE")
        frm.set_df_property('progress_bar', 'options', "<div><div>")
        frm.refresh_field('progress_bar')         
    } 
}

function make_attachment_mandatory_based_on_condition(frm){

    let attachment_mandatory = false
    if (frm.doc.leave_category === "Sick"){
        attachment_mandatory = true
    }

    if (frm.doc.leave_type){
        frappe.db.get_value('Leave Type', frm.doc.leave_type, 'custom_attachment_required')
            .then(r => {
                // console.log(r, "-------------r")
                if (r.message.custom_attachment_required){
                    attachment_mandatory = true
                }
            })
        }

    if (attachment_mandatory){
        frm.set_df_property("attachment", "reqd", 1)
    }
    else{
        frm.set_df_property("attachment", "reqd", 0)
    }
}
