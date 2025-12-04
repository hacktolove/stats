// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Attendance Checkup ST", {
    onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
            .then(r => {
                let values = r.message;
                frm.set_value('created_by', values.name)
            })
        }  
    },
    setup(frm) {
        frm.set_query("main_department", function (doc) {
            return {
                query: "stats.api.get_main_department",
            };
        });
        frm.set_query("sub_department", function (doc) {
            if (frm.doc.main_department) {
                return {
                    filters: {
                        parent_department: frm.doc.main_department,
                        is_group: 0
                    }
                };
            }
        })
    },
    fetch_employee(frm) {
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("employee_attendance_checkup_details", "");
        frm.call("fetch_employees").then((r) => {
            let employee_list = r.message
            if (employee_list.length > 0) {
                employee_list.forEach((ele) => {
                    var d = frm.add_child("employee_attendance_checkup_details");
                    frappe.model.set_value(d.doctype, d.name, "employee_no", ele.name)
                    frappe.model.set_value(d.doctype, d.name, "actual_attendance", "")
                })
                frm.refresh_field('employee_attendance_checkup_details')
                frm.save()
            }
        })
    },
    fetch_attendance(frm) {
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.call("fetch_attendances").then((r) => {
            let checkin_list = r.message
            let employee_attendance_checkup_details = frm.doc.employee_attendance_checkup_details
            if (checkin_list.length > 0) {
                checkin_list.forEach((ele) => {
                    if (employee_attendance_checkup_details.length > 0) {
                        employee_attendance_checkup_details.forEach((row) => {
                            if (row.employee_no == ele.employee) {
                                frappe.model.set_value(row.doctype, row.name, "actual_attendance", ele.time)
                            }
                        })
                    }
                })
                frm.refresh_field('employee_attendance_checkup_details')
                frm.save('Update')
            }
        })
    }
});
