// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Overtime Request ST", {
	onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['name','department','custom_sub_department'])
            .then(r => {
                let values = r.message;
                console.log(values,"---")
                frm.set_value('employee', values.name)
                frm.set_value('main_department', values.department)
                frm.set_value('sub_department', values.custom_sub_department)
            })
        }  
    },
    onload_post_render(frm) {
        if (frm.doc.overtime_end_date) {
            if (frappe.datetime.add_days(frm.doc.overtime_end_date, 1) <= frappe.datetime.nowdate()) {
                frm.add_custom_button(__('Overtime Approval Request'), () => create_overtime_approval_request(frm));
            }
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
    fetch_employee(frm){
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }
        if (frm.doc.docstatus==0){
        frm.set_value("employee_overtime_request", "");
        frm.call({
            doc: frm.doc,
            method: "get_employee",
            freeze: true,
            callback: (r) => {
                let employee_list = r.message
                console.log(employee_list, '--list')
                if (employee_list) {
                    employee_list.forEach((e) => {
                        var d = frm.add_child("employee_overtime_request");
                        frappe.model.set_value(d.doctype, d.name, "employee_no", e.employee_no)
                        frappe.model.set_value(d.doctype, d.name, "employee_name", e.employee_name)
                        frappe.model.set_value(d.doctype, d.name, "total_no_of_days", frm.doc.total_no_of_days)
                    });
                    refresh_field("employee_overtime_request");
                    // frm.save()
                }
            },
        });
    }
    }
});

let create_overtime_approval_request = function(frm) {
    if (frm.is_dirty() == true) {
        frappe.throw({
            message: __("Please save the form to proceed..."),
            indicator: "red",
        });
    }

    frappe.call({
        method: "stats.stats.doctype.overtime_request_st.overtime_request_st.create_overtime_approval_request",
        args: {
            source_name: frm.doc.name
        },
        callback: function (r) {
            if (r.message) {
                window.open(`/app/overtime-approval-request-st/` + r.message);
            }
        }
    })
}