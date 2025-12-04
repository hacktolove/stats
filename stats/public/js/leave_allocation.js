frappe.ui.form.on("Leave Allocation", {
    refresh: function(frm){
        frm.set_query("leave_type", function(){
            return {
                filters: {
                    "custom_based_on_leave_request":0,
                    "is_lwp":0
                }
            }
        })
    }
})