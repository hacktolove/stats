frappe.ui.form.on("ToDo", {
    status: function (frm) {
        if(frm.doc.status == "Closed"){
            frm.set_value("custom_date_of_completion", frappe.datetime.nowdate());
        }
        else{
            frm.set_value("custom_date_of_completion", '');
        }
    }
})