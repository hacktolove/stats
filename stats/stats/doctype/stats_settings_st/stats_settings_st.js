// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stats Settings ST", {
	onload: function (frm) {
		frm.set_query("default_budget_account", function () {
			return {
				filters: {
					company: frm.doc.company,
					report_type: "Profit and Loss",
					is_group: 0,
				},
			};
		});
	},
});
