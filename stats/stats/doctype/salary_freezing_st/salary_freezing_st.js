// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Salary Freezing ST", {
	refresh(frm) {
        if(frm.doc.docstatus == 1 && !frm.doc.freezing_end_type){
            frm.add_custom_button(__('End Freezing'), () => employee_end_freezing(frm));
        } 
	},
});

let employee_end_freezing = function (frm) {
    let dialog = undefined
    const dialog_field = []

    dialog_field.push(
        {
            fieldtype: "Select",
            fieldname: "freezing_end_type",
            label: __("Freezing End Type"),
            options:[__("Separation"), __("Reactivation"), __("Superior Reactivation")],
            default: "Separation",
            reqd: 1,
            onchange: function(){
                let end_type = dialog.get_field("freezing_end_type")
                console.log(end_type, "==================end_type=========")
                // if (end_type.value == "Separation"){
                //     dialog.set_df_property('salary_freezing_end_date','hidden',1)
                //     dialog.set_df_property('salary_freezing_end_date','reqd',0)
                // }
                // else{
                //     dialog.set_df_property('salary_freezing_end_date','hidden',0)
                //     dialog.set_df_property('salary_freezing_end_date','',1)
                // }
            }
        },
        {
            fieldtype: "Date",
            fieldname: "salary_freezing_end_date",
            label: __("Salary Freezing End Date"),
            hidden: 0,
            default: frm.doc.salary_freezing_end_date || '',
            reqd: 1,
            onchange: function(){
                let end_date = dialog.get_field("salary_freezing_end_date")
                if (end_date.value) {
                    frm.set_value("salary_freezing_end_date", end_date.value).then(() => {frm.call("validate_salary_freezing_dates") })
                }
            }
        }
    )

    dialog = new frappe.ui.Dialog({
        title: __("End Salary Freezing"),
        fields: dialog_field,
        primary_action_label: 'End Salary Freezing',
        primary_action: function (values) {
            frappe.call({
                method: "end_salary_freezing",
                doc: frm.doc,
                args: {
                    "freezing_end_type": values.freezing_end_type,
                    "freezing_end_date": values.salary_freezing_end_date || undefined
                },
                callback: function (r) {
                //    refresh_field("freezing_end_type");
                   frm.refresh()
                }
            });
            dialog.hide();
        }
    })
    dialog.show()
}