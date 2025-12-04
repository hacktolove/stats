// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Change Request ST", {
    refresh: function (frm) {
        if (!frm.is_new()) {
			frm.add_custom_button(
				__("Used Budget"),
				function () {
					frappe.route_options = {
					from_fiscal_year:frm.doc.fiscal_year,
					to_fiscal_year: frm.doc.fiscal_year,
					period:'Yearly',
					company:frappe.defaults.get_default("company"),
					budget_against:"Cost Center",
					// budget_against_filter:frm.doc.cost_center
				};
				frappe.set_route("query-report", "Budget Variance Report");
				});
		}
        else{
            frm.set_value('fiscal_year', erpnext.utils.get_fiscal_year(frappe.datetime.get_today()))
        }
    },
	onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
            .then(r => {
                let values = r.message;
                frm.set_value('employee', values.name)
            })
        }  
    },
    setup(frm) {
        frm.set_query("to_account", function () {
            return {
                query: "stats.stats.doctype.budget_change_request_st.budget_change_request_st.get_budget_account_for_budget_change_request",
                filters:{
                    main_department: frm.doc.to_main_department,
                    fiscal_year: frm.doc.fiscal_year
                }
            };
        }),
        frm.set_query("from_account", function () {
            return {
                query: "stats.stats.doctype.budget_change_request_st.budget_change_request_st.get_budget_account_for_budget_change_request",
                filters:{
                    main_department: frm.doc.from_main_department,
                    fiscal_year: frm.doc.fiscal_year
                }
            };
        }),
        frm.set_query("from_main_department", function (doc) {
            return {
                query: "stats.api.get_main_department",
            };
        }),
        frm.set_query("to_main_department", function (doc) {
            return {
                query: "stats.api.get_main_department",
            };
        })
    }
});
