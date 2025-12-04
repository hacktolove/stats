frappe.ui.form.on("Leave Type", {
    setup(frm) {
        frm.set_query("custom_allow_after_consuming_balance_for", function() {
            return {
                query: "stats.hr_utils.get_leave_type_for_allow_after_consuming_balance"
            }
        })
    },
})