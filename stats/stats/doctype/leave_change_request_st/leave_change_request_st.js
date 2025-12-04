// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Change Request ST", {
    setup(frm) {
        frm.set_query("leave_application_reference", function (doc) {
            return {
                filters: {
                'employee': frm.doc.employee_no,
                'docstatus': 1
                }
            }
         })
    },
});
