// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Achievement Certificate ST", {
    setup(frm) {
        frm.set_query("reference_type", function (doc) {
            return {
                filters: {
                    "name": ["in", ["International Subscription Payment Request ST", "Purchase Invoice", "Purchase Order"]]
                }
            };
        })
    },

    invoice_amount(frm) {
        calculate_tax_on_invoice_amount(frm)
    },

    calculate_tax(frm) {
        calculate_tax_on_invoice_amount(frm)
    },

    penalty_amount(frm) {
        calculate_tax_on_invoice_amount(frm)
    }
});

let calculate_tax_on_invoice_amount = function(frm){
    let penalty_amount = frm.doc.penalty_amount ? frm.doc.penalty_amount : 0
    if (frm.doc.calculate_tax == 1) {
        frm.call("calculate_tax_on_invoice_amount")
        .then((r) => {
            console.log(r.message,"calculate_tax_on_invoice_amount")
            let tax_amount = r.message
            let final_amount = frm.doc.invoice_amount+tax_amount-penalty_amount
            let money_in_words = frappe.tafqeet(final_amount,"SAR")
            console.log(tax_amount,"=====tax_amount")
            frm.set_value("tax_amount",tax_amount)
            frm.set_value("final_amount",final_amount)
            frm.set_value("amount_in_words",money_in_words)

        })
    }
    else {
        let final_amount = frm.doc.invoice_amount-penalty_amount
        frm.set_value("final_amount",final_amount)
        frm.set_value("amount_in_words",frappe.tafqeet(frm.doc.final_amount,"SAR"))
    }
}