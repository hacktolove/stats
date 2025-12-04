// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Retirement Request ST", {
	refresh(frm) {
        if(frm.doc.docstatus==1){
            frm.add_custom_button(__('Retirement Request'), () => create_retirement_request(frm));
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
        })
    },
});

let create_retirement_request = function (frm) {
    if (frm.is_dirty() == true) {
        frappe.throw({
            message: __("Please save the form to proceed..."),
            indicator: "red",
        });
    }

    frm.call("create_retirement_request").then((r) => {
        if (r.message) {
            console.log(r.message, "r.message")
            frappe.open_in_new_tab = true;
            frappe.set_route("Form", "Retirement Request ST", r.message);
            // window.open(`app/end-of-service-calculation-st/` + r.message);
        }
    })
}