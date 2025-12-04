// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Onboarding ST", {
	employee_onboarding_template: function (frm) {
		frm.set_value("onboarding_procedures", "");
		if (frm.doc.employee_onboarding_template) {
			frappe.call({
				method: "stats.stats.doctype.employee_onboarding_st.employee_onboarding_st.get_onboarding_details",
				args: {
					parent: frm.doc.employee_onboarding_template,
					parenttype: "Employee Onboarding Template ST",
				},
				callback: function (r) {
					if (r.message) {
						r.message.forEach((d) => {
							frm.add_child("onboarding_procedures", d);
						});
						refresh_field("onboarding_procedures");
					}
				},
			});
		}
	},
});
