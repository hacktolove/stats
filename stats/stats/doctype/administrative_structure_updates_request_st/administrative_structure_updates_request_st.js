// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Administrative Structure Updates Request ST", {

    onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department', 'custom_sub_department'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('created_by', values.employee_name)
                    frm.set_value('main_department', values.department)
                    frm.set_value('sub_department', values.custom_sub_department)
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
        frm.set_query("parent_department", function (doc) {
            return {
                filters: {
                    is_group: 1
                }
            };
        });
        frm.set_query("existing_main_department_1", function (doc) {
            return {
                filters: {
                    is_group: 1
                }
            };
        });
        frm.set_query("existing_main_department_2", function (doc) {
            return {
                filters: {
                    is_group: 1
                }
            };
        });
        frm.set_query("existing_sub_department_1", function (doc) {
            return {
                filters: {
                    is_group: 0
                }
            };
        });
        frm.set_query("existing_sub_department_2", function (doc) {
            return {
                filters: {
                    is_group: 0
                }
            };
        });
    },

    request_type(frm) {
        set_options_for_request_type(frm)
    },

    existing_main_department_1(frm) {
        console.log("-------")
        frappe.db.get_value('Department', frm.doc.existing_main_department_1 , 'parent_department')
                .then(r => {
                console.log(r.message.parent_department)
                let parent_department = r.message.parent_department
                if (parent_department) {
                    frm.set_value("parent_department_name_1",parent_department)
                }
                })
    },

    existing_main_department_2(frm) {
        console.log("-------")
        frappe.db.get_value('Department', frm.doc.existing_main_department_2 , 'parent_department')
                .then(r => {
                console.log(r.message.parent_department)
                let parent_department = r.message.parent_department
                if (parent_department) {
                    frm.set_value("parent_department_name_2",parent_department)
                }
                })
    },

    existing_sub_department_1(frm) {
        console.log("-------")
        frappe.db.get_value('Department', frm.doc.existing_sub_department_1 , 'parent_department')
                .then(r => {
                console.log(r.message.parent_department)
                let parent_department = r.message.parent_department
                if (parent_department) {
                    frm.set_value("parent_department_name_1",parent_department)
                }
                })
    },

    existing_sub_department_2(frm) {
        console.log("-------")
        frappe.db.get_value('Department', frm.doc.existing_sub_department_2 , 'parent_department')
                .then(r => {
                console.log(r.message.parent_department)
                let parent_department = r.message.parent_department
                if (parent_department) {
                    frm.set_value("parent_department_name_2",parent_department)
                }
                })
    },

});

let set_options_for_request_type = function (frm) {
    let options = [""]
    if (frm.doc.request_type == "Create New Department") {
        options = [
            "",
            "Create New Main Department",
            "Create New Sub Department",
            "Create New Unit"
        ];
    }
    if (frm.doc.request_type == "Merge Department") {
        options = [
            "",
            "Merge Main Department",
            "Merge Sub Department",
            "Merge Unit"
        ];
    }
    if (frm.doc.request_type == "Separate Department") {
        options = [
            "",
            "Separate Main Department",
            "Separate Sub Department",
            "Separate Unit"
        ];
    }

    set_field_options("type", options.join("\n"));
}