// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Breast Feeding Request ST", {
    setup(frm) {
        frm.set_query("employee_no", function(frm){
            return {
                filters: {
                    status: "Active",
                    gender: __("Female")
                }
            }
        })
    }
});