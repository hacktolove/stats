
let is_form_load_event_bound = false;
console.log(is_form_load_event_bound, "=============is_form_load_event_bound==========")
$(document).on("form-load", function (event, frm) {


    if (is_form_load_event_bound == false) {
        is_form_load_event_bound = true;

        console.log("--------Form Load---------------", frm.doc.doctype)
        // if ($('div.modal-dialog textarea[data-fieldname="reject_reason"]').length == 0){
        if (frappe.meta.has_field(frm.doc.doctype, "workflow_state")) {
            let prev_workflow_state = ''
            frappe.ui.form.on(frm.doc.doctype, {
                before_workflow_action(frm){
                    prev_workflow_state = frm.doc.workflow_state
                    console.log("------prev_workflow_state---------------", prev_workflow_state)
                },
                after_workflow_action(frm) {
                    console.log("--------After Workflow Action---------------", frm.doc.workflow_state)
                    // console.log($('div.modal-dialog textarea[data-fieldname="reject_reason"]').length, "==========length")

                    frappe.call({
                        method: "stats.api.check_action_is_rejected",
                        args: {
                            doctype: frm.doc.doctype,
                            prev_workflow_state: prev_workflow_state,
                            workflow_state: frm.doc.workflow_state
                        },
                        callback: function (r) {
                            console.log(r.message, "r")
                            let is_rejected = r.message

                            if (is_rejected) {
                                frappe.prompt({
                                    label: 'Reject Reason',
                                    fieldname: 'reject_reason',
                                    fieldtype: 'Small Text',
                                    reqd: 1
                                },
                                    (values) => {
                                        console.log(values.reject_reason);
                                        frappe.call({
                                            method: "stats.api.add_reject_reason",
                                            args: {
                                                doctype: frm.doc.doctype,
                                                docname: frm.doc.name,
                                                reject_reason: values.reject_reason
                                            },
                                            callback: function (r) {
                                                console.log(r.message, "r")
                                            }
                                        })
                                    })
                            }
                        }
                    })
                }
            })
            // }
        }
    }

})