// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Task Completion ST", {
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
		})
    },

    trip_cost_template: function (frm) {
        frm.set_value("trip_cost_detail", "");
        frm.call("fetch_trip_cost_details_from_template").then(r => {
            let trip_cost_details = r.message
            console.log(trip_cost_details,"============")
            trip_cost_details.forEach((element) => {
                var d = frm.add_child("trip_cost_detail");
                frappe.model.set_value(d.doctype, d.name, "element", element.element)
                frappe.model.set_value(d.doctype, d.name, "payment_method", element.payment_method)
            });
            refresh_field("trip_cost_detail");
        })

    }
});
