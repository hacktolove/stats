// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("End of Service Calculation ST", {
    validate(frm) {
        frm.set_value("total_due_amount_in_words", frappe.tafqeet((frm.doc.vacation_due_amount + frm.doc.end_of_service_due_amount), "SAR"))
    },
});
