// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Evaluation ST", {

    setup: function (frm) {
        frm.trigger("hide_grid_add_row");
    },

    hide_grid_add_row: function (frm) {
        setTimeout(() => {
            frm.fields_dict.employee_personal_goals.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.employee_job_goals.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.basic_competencies.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.technical_competencies.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.leadership.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.employee_personal_goals.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.employee_job_goals.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.basic_competencies.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.technical_competencies.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.leadership.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);
    },

    fetch_goals(frm) {
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("employee_personal_goals", "");
        frm.set_value("employee_job_goals", "")
        frm.set_value("basic_competencies", "")
        frm.set_value("technical_competencies", "")
        frm.set_value("leadership", "")

        frm.call("fetch_employee_different_goals").then((r) => {
            console.log(r, "r")
            let employee_personal_goals = r.message[0]
            let employee_job_goals = r.message[1]
            let basic_competencies = r.message[2]
            let technical_competencies = r.message[3]
            let leadership = r.message[4]

            frappe.db.get_single_value('Stats Settings ST', 'degree_out_of')
            .then(degree_out_of => {
                console.log(degree_out_of,"=============");
            if (employee_personal_goals) {
                employee_personal_goals.forEach((ele) => {
                    var d = frm.add_child("employee_personal_goals");
                    frappe.model.set_value(d.doctype, d.name, "goals", ele.goals)
                    frappe.model.set_value(d.doctype, d.name, "weight", ele.weight)
                    frappe.model.set_value(d.doctype, d.name, "target_degree", ele.target_degree)
                })
                frm.refresh_field('employee_personal_goals')
            }

            if (employee_job_goals) {
                employee_job_goals.forEach((ele) => {
                    var d = frm.add_child("employee_job_goals");
                    frappe.model.set_value(d.doctype, d.name, "goals", ele.goals)
                    frappe.model.set_value(d.doctype, d.name, "weight", ele.weight)
                    frappe.model.set_value(d.doctype, d.name, "uom", ele.uom)
                    frappe.model.set_value(d.doctype, d.name, "target_degree", ele.target_degree)
                })
                frm.refresh_field('employee_job_goals')
            }
                if (degree_out_of > 0) {
                    if (basic_competencies) {
                        console.log(basic_competencies, "basic_competencies")
                        basic_competencies.forEach((ele) => {
                            var d = frm.add_child("basic_competencies");
                            frappe.model.set_value(d.doctype, d.name, "competencies_name", ele.competencies_name)
                            frappe.model.set_value(d.doctype, d.name, "description", ele.description)
                            frappe.model.set_value(d.doctype, d.name, "weight", ele.weight)
                            frappe.model.set_value(d.doctype, d.name, "degree_out_of_5", degree_out_of)
                        })
                        frm.refresh_field('basic_competencies')
                    }

                    if (technical_competencies) {
                        technical_competencies.forEach((ele) => {
                            var d = frm.add_child("technical_competencies");
                            frappe.model.set_value(d.doctype, d.name, "competencies_name", ele.competencies_name)
                            frappe.model.set_value(d.doctype, d.name, "description", ele.description)
                            frappe.model.set_value(d.doctype, d.name, "weight", ele.weight)
                            frappe.model.set_value(d.doctype, d.name, "degree_out_of_5", degree_out_of)
                        })
                        frm.refresh_field('technical_competencies')
                    }

                    if (leadership) {
                        leadership.forEach((ele) => {
                            var d = frm.add_child("leadership");
                            frappe.model.set_value(d.doctype, d.name, "competencies_name", ele.competencies_name)
                            frappe.model.set_value(d.doctype, d.name, "description", ele.description)
                            frappe.model.set_value(d.doctype, d.name, "weight", ele.weight)
                            frappe.model.set_value(d.doctype, d.name, "degree_out_of_5", degree_out_of)
                        })
                        frm.refresh_field('leadership')
                    }
                } else {
                    frappe.throw(__("Please set 'Degree Out Of' in Stats Settings ST"))
                }
            })

            frm.save()
        })
    },

});

frappe.ui.form.on("Employee Personal Goals Details ST", {
    actual_degree(frm, cdt, cdn) {
        calculate_degree_based_on_weight(frm, cdt, cdn)
    }
});

frappe.ui.form.on("Employee Job Goals Details ST", {
    actual_degree(frm, cdt, cdn) {
        calculate_degree_based_on_weight(frm, cdt, cdn)
    }
});

frappe.ui.form.on("Employee Competencies Details ST", {
    actual_degree(frm, cdt, cdn) {
        calculate_degree_based_on_weight(frm, cdt, cdn)
    }
});

let calculate_degree_based_on_weight = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    if (row.actual_degree && row.weight) {
        let actual_degree_based_on_weight = (row.actual_degree * row.weight) / 100
        frappe.model.set_value(cdt, cdn, "actual_degree_based_on_weight", actual_degree_based_on_weight)
    }
}
