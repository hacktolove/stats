// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Department Budget ST", {
    refresh: function (frm) {
        if (frm.doc.budget_update.length > 0) {
			frm.add_custom_button(
				__("Used Budget"),
				function () {
					frappe.route_options = {
					from_fiscal_year:frm.doc.fiscal_year,
					to_fiscal_year: frm.doc.fiscal_year,
					period:'Yearly',
					company:frappe.defaults.get_default("company"),
					budget_against:"Cost Center",
					budget_against_filter:frm.doc.cost_center
				};
				frappe.set_route("query-report", "Budget Variance Report");
				});
		}
    },
    onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
            .then(r => {
                let values = r.message;
                frm.set_value('requested_by', values.name)
            })
            frm.set_value('fiscal_year', erpnext.utils.get_fiscal_year(frappe.datetime.get_today()))
        }  
    },
    setup(frm) {
        frm.set_query("budget_expense_account","account_table", function (doc,cdt,cdn) {
            const default_company = frappe.defaults.get_default("company");
            return {
                filters: {
                    "company": default_company,
                    "is_group": 0,
                    "account_type": ["in",["Expense Account", "Indirect Expense"]]
                }
            };
            // return {
            //     query: "stats.stats.doctype.department_budget_st.department_budget_st.get_budget_account",
            // };
        }),
        frm.set_query("main_department", function (doc) {
            return {
                query: "stats.api.get_main_department",
            };
        })
    }
});
