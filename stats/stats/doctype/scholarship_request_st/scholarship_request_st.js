// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Scholarship Request ST", {
    setup(frm) {
        frm.set_query("scholarship_no",function (doc){
            return {
                query: "stats.stats.doctype.scholarship_request_st.scholarship_request_st.get_open_scholarships"
            };
        });
        frm.set_query("specialisation_type", function(doc){
            if (frm.doc.scholarship_no){
                return {
                    query:"stats.stats.doctype.scholarship_request_st.scholarship_request_st.get_specialisation_type_from_scholarship_no",
                    filters : {
                        scholarship_no : frm.doc.scholarship_no
                    }
                }
            }
        })
    },

    refresh(frm) {
        if (frm.doc.docstatus == 1 && frm.doc.acceptance_status == "Accepted") {
            frm.add_custom_button(__('Extend Scholarship'), () => create_extend_scholarship_from_request(frm), __("Create"));
            frm.add_custom_button(__('Return From Scholarship'), () => create_return_from_scholarship(frm), __("Create"));
        }
    },

    onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
                .then(r => {
                    let values = r.message;
                    frm.set_value('employee_no', values.name)
                })
        }
    },

    specialisation_type(frm) {
        if (frm.doc.specialisation_type) {
            frm.call("fetch_scholarship_details_based_on_specialisation_type").then((r) => {
                let scholarship_terms = r.message[1]
                let scholarship_detail_list = r.message[0]
                if (scholarship_detail_list.length > 0) {
                    frm.set_value("qualification", scholarship_detail_list[0].qualification)
                    frm.set_value("english_required", scholarship_detail_list[0].english_required)
                    frm.set_value("terms_and_conditions",scholarship_terms)
                }
            })
        }
    }
});

function create_extend_scholarship_from_request (frm) {
    frappe.model.open_mapped_doc({
        method: "stats.stats.doctype.scholarship_request_st.scholarship_request_st.create_extend_scholarship_from_request",
        frm: frm
    });
}

function create_return_from_scholarship (frm) {
    frappe.model.open_mapped_doc({
        method: "stats.stats.doctype.scholarship_request_st.scholarship_request_st.create_return_from_scholarship",
        frm: frm
    });
}