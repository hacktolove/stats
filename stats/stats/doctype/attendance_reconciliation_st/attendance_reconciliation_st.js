// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Reconciliation ST", {
    onload(frm) {
        let month = frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()
        console.log(month,"-=-")
    },

    setup: function (frm) {
        frm.trigger("hide_grid_add_row");
    },

    hide_grid_add_row: function (frm) {
        setTimeout(() => {
            frm.fields_dict.attendance_reconciliation_details.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.attendance_reconciliation_details.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);
    },

    employee_no(frm){
        let employee = frm.doc.employee_no
        frappe.db.get_value('Employee', employee, 'custom_contract_type')
            .then(r => {
            let contract_type = r.message.custom_contract_type
            frappe.db.get_value("Contract Type ST",contract_type,"contract")
                .then(response=> {
                    let contract = response.message.contract
                    if (contract == "Civil"){
                        frappe.db.get_value("Contract Type ST",contract_type,"permission_balance_per_month")
                            .then(r => {
                                let permission_balance_per_month = r.message.permission_balance_per_month
                                frm.set_value("total_available_permission_balance",permission_balance_per_month)
                            })
                    }
                    else if (contract == "Direct"){
                        frappe.db.get_value('Employee', employee, 'custom_permission_balance_per_year')
                            .then(r => {
                                let permission_balance_per_year = r.message.custom_permission_balance_per_year
                                frm.set_value("total_available_permission_balance",permission_balance_per_year)
                            })
                    }
                })
            })
    },

    fetch(frm) {
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("attendance_reconciliation_details", "");
        frm.call("fetch_attendance_details").then((r) => {
            let reconciliation_data = r.message
            if (reconciliation_data.length > 0) {
                reconciliation_data.forEach((ele) => {
                    var d = frm.add_child("attendance_reconciliation_details");
                    frappe.model.set_value(d.doctype, d.name, "date", ele.date)
                    frappe.model.set_value(d.doctype, d.name, "type", ele.type)
                    frappe.model.set_value(d.doctype, d.name, "delay_in", ele.delay_in)
                    frappe.model.set_value(d.doctype, d.name, "early_out", ele.early_out)
                    frappe.model.set_value(d.doctype, d.name, "expected_working_minutes", ele.expected_working_minutes)
                    frappe.model.set_value(d.doctype, d.name, "actual_working_minutes", ele.actual_working_minutes)
                    frappe.model.set_value(d.doctype, d.name, "shortfall_in_working_minutes", ele.shortfall_in_working_minutes)
                    frappe.model.set_value(d.doctype, d.name, "day", ele.day)
                    frappe.model.set_value(d.doctype, d.name, "attendance_reference", ele.attendance_reference)
                })
                frm.refresh_field('attendance_reconciliation_details')
                frm.save()
            }
        })
    }
});


frappe.ui.form.on("Attendance Reconciliation Details ST", {
    reason (frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        if (row.reason == "Deduct From Permission Balance") {
            if (row.shortfall_in_working_minutes >= 0){
                frappe.model.set_value(cdt, cdn, "balance_to_be_consumed_in_minutes",row.shortfall_in_working_minutes)
            }else{
                frappe.model.set_value(cdt, cdn, "balance_to_be_consumed_in_minutes",-(row.shortfall_in_working_minutes))
            }
        }
    }
})