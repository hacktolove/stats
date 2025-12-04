// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Personal Training Request ST", {
	training_start_date(frm) {
        set_no_of_days(frm)
	},
    training_end_date(frm){
        set_no_of_days(frm)
    },
    ignore_holidays_in_no_of_days(frm){
        set_no_of_days(frm)
    }
});

let set_no_of_days = function (frm) {
    let start_date = frm.doc.training_start_date
    let end_date = frm.doc.training_end_date
    if (start_date && end_date) {
        let no_of_day = frappe.datetime.get_day_diff(end_date, start_date)
        if (frm.doc.ignore_holidays_in_no_of_days == 1){
            console.log("------------")
            frm.call("check_holiday_between_start_end_date").then(
                r => {
                    console.log(r.message)
                    holiday_count = r.message
                    frm.set_value("no_of_days", (no_of_day-holiday_count || 0)+1)
                }
            )
        }
        else{
            frm.set_value("no_of_days", (no_of_day || 0)+1)
        }
        frm.set_value("no_of_days", (no_of_day || 0)+1)
    }
}