frappe.ui.form.on("Department", {
    onload(frm) {
        frm.set_query("custom_department_cost_center", function (doc) {
            return {
                filters: {
                    "company": frm.doc.company,
                    "is_group": 0,
                    "disabled": 0
                }
            };
        })
    }
})