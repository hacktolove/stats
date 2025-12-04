// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Request ST", {
    setup(frm) {
        frm.set_value("created_by", frappe.session.user_fullname)

        frm.set_query("event", function (doc) {
            return {
               query: 'stats.stats.doctype.event_request_st.event_request_st.get_ongoing_events_as_per_request_creation_date',
               filters: {
                    'docstatus' : 1,
                    'creation_date' : frm.doc.creation_date
               }
            }
        })

        frm.set_query("employee", "gm_details", function(doc) {
            return {
                query: 'stats.stats.doctype.event_request_st.event_request_st.filter_employees_based_on_logged_in_user',
                filters: {
                    'reports_to' : frappe.session.user_email
                }
            }
        })

        frm.set_query("employee", "department_manager_details", function(doc) {
            return {
                query: 'stats.stats.doctype.event_request_st.event_request_st.filter_employees_based_on_logged_in_user',
                filters: {
                    'reports_to' : frappe.session.user_email
                }
            }
        })

        frm.set_query("employee", "candidate_details", function(doc) {
            return {
                query: 'stats.stats.doctype.event_request_st.event_request_st.filter_employees_based_on_logged_in_user',
                filters: {
                    'reports_to' : frappe.session.user_email
                }
            }
        })
    },

    event(frm) {
        let event = frm.doc.event;
        if (event != null) {
            frappe.db.get_value("Event ST", event, "section").then((res) => {
                frm.set_value("section", res.message.section)
            });

            frappe.db.get_value("Event ST", event, "no_of_candidates").then((res) => {
                frm.set_value("no_of_candidates", res.message.no_of_candidates)
            })
        }
    },
});