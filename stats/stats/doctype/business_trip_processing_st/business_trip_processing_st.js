// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Business Trip Processing ST", {
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

    refresh(frm) {
        if (!frm.is_new() && (frm.doc.business_trip_detail).length < 1) {
            frm.add_custom_button(__('Fetch Business Trips'), () => fetch_business_trips_from_business_trip_request(frm));
        }     
    }
});

frappe.ui.form.on("Business Trip Processing Multi Direction Details ST", {
    from_date(frm, cdt, cdn) {
        calculate_no_of_days_in_multi_direction(frm, cdt, cdn)
    },
    to_date(frm, cdt, cdn) {
        calculate_no_of_days_in_multi_direction(frm, cdt, cdn)
    }
})

let fetch_business_trips_from_business_trip_request = function (frm) {
    if (frm.is_dirty() == true) {
        frappe.throw({
            message: __("Please save the form to proceed..."),
            indicator: "red",
        });
    }
    frappe.call({
        method: "stats.stats.doctype.business_trip_processing_st.business_trip_processing_st.fetch_business_trip_request",
        args: {
            name: frm.doc.name
        },
        callback: function (r) {
            let business_trip_list = r.message
            if (business_trip_list.length > 0){
                business_trip_list.forEach((ele) => {
                    var d = frm.add_child("business_trip_detail");
                    frappe.model.set_value(d.doctype, d.name, "business_trip_reference", ele.name)
                })
                frm.refresh_field('business_trip_detail')
                frm.save()
            }
        }
    })
}

let calculate_no_of_days_in_multi_direction = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    let no_of_day = frappe.datetime.get_day_diff(row.to_date, row.from_date)
    frappe.model.set_value(row.doctype, row.name,"no_of_days", no_of_day)
    }