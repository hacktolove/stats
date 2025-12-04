// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Work Out of Office ST", {
	onload(frm) {
        frm.set_query("deputy_employee", function () {
                return {
                    query: "stats.api.get_deputy_employee_list",
                    filters: {
                        employee: frm.doc.employee_no
                    }
                };
        });
    },
});
