// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Evaluation Template ST", {

});

frappe.ui.form.on("Job Goals Details ST", {
    weight(frm, cdt, cdn) {
        set_degree_based_on_weight(frm, cdt, cdn)
    },

    target_degree(frm, cdt, cdn) {
        set_degree_based_on_weight(frm, cdt, cdn)
    }
})

let set_degree_based_on_weight = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    if (row.weight && row.target_degree) {
        let degree_based_on_weight = (row.weight * row.target_degree) / 100
        frappe.model.set_value(cdt, cdn, "degree_based_on_weight", degree_based_on_weight)
    }
}
