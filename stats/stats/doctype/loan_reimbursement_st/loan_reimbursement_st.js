// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Loan Reimbursement ST", {
	refresh(frm) {
         setTimeout(() => {
            frm.fields_dict.table_of_discounts.grid.wrapper.find(".grid-add-row").remove();
            frm.fields_dict.table_of_discounts.grid.wrapper.find(".grid-remove-rows").remove();
        }, 100);
	},
});
