frappe.ui.form.on("Employee", {
    refresh(frm) {
        setTimeout(() => {
            set_is_manager_from_designation_in_new_employee(frm)
            // set_report_to_for_employee(frm)
        }, 200);
        console.log("in setup")
        frm.set_query("department", function (doc) {
            console.log("Working")
            return {
                query: "stats.api.get_main_department",
            };
        });
        frm.set_query("custom_sub_department", function (doc) {
            if (frm.doc.department) {
                return {
                    query: "stats.api.get_descendant_departments",
                    filters: {
                        main_department: frm.doc.department,
                    }
                };
            }
        })
    },
    custom_is_manager: function (frm) {
        // set_report_to_for_employee(frm)
    },
    department: function (frm) {
        // set_report_to_for_employee(frm)
    },
    custom_sub_department: function (frm) {
        // set_report_to_for_employee(frm)
    },
    designation: function (frm) {
        set_is_manager_from_designation_in_new_employee(frm)
    }
})

let set_report_to_for_employee = function (frm) {
    if (frm.doc.custom_is_manager == 1) {
        if (frm.doc.department) {
            frappe.db.get_value('Department', frm.doc.department, 'custom_main_department_manager')
                .then(r => {
                    console.log(r.message.custom_main_department_manager)
                    frm.set_value('reports_to', r.message.custom_main_department_manager || "")
                })
        }
    }
    else {
        if (frm.doc.custom_sub_department) {
            frappe.db.get_value('Department', frm.doc.custom_sub_department, 'custom_direct_manager')
                .then(r => {
                    console.log(r.message.custom_direct_manager)
                    frm.set_value('reports_to', r.message.custom_direct_manager || "")
                })
        }
    }
}

let set_is_manager_from_designation_in_new_employee = function(frm) {
    if (frm.doc.designation) {
        if (frm.is_new()){
            frappe.db.get_value('Designation', frm.doc.designation, 'custom_is_manager')
                .then(r => {
                    frm.set_value('custom_is_manager', r.message.custom_is_manager || 0)
                })
        }
    }
    if (!frm.doc.designation && frm.is_new()){
        frm.set_value('custom_is_manager', 0)
    }
}