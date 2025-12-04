// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event ST", {
    event_start_date(frm) {
        calculate_no_of_days(frm);
    },

    event_end_date(frm) {
        calculate_no_of_days(frm);
    },

    ignore_holidays_in_number_of_days(frm) {
        calculate_no_of_days(frm);
    }
});

function calculate_no_of_days(frm) {
    let event_start_date = frm.doc.event_start_date;
    let event_end_date = frm.doc.event_end_date;
    let ignore_holidays_in_number_of_days = frm.doc.ignore_holidays_in_number_of_days;

    if (event_start_date != null && event_end_date != null) {
        frm.call({
            method: 'calculate_event_days',
            args: {
                'event_start_date': event_start_date,
                'event_end_date': event_end_date,
                'ignore_holidays_in_number_of_days': ignore_holidays_in_number_of_days,
            },
            callback: function(res) {
                frm.set_value("no_of_days", res.message)
            }
        })
    }
}