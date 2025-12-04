frappe.ui.form.on("Payroll Entry", {
    refresh(frm) {
        if (frm.is_new() || frm.doc.employees.length == 0 || frm.doc.docstatus == 1) {
            frm.set_df_property('custom_generate_deductions', 'hidden', 1)
        }
        else {
            frm.set_df_property('custom_generate_deductions', 'hidden', 0)
        }
    },
    custom_generate_deductions: function (frm) {
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }
        else {
            // lwp deduction
            frappe.call({
                method: "stats.salary.calculate_lwp_dedution",
                args: {
                    payroll_entry: frm.doc.name
                },
                callback: function (r) {
                    console.log(r.message, '--r.message')
                    let lwp_deduction_list = r.message
                    if (lwp_deduction_list.length > 0) {
                        lwp_deduction_list.forEach((ele) => {
                            frm.doc.employees.forEach((row) => {
                                if (ele.employee == row.employee)
                                    frappe.model.set_value(row.doctype, row.name, "custom_lwp_deduction", ele.lwp_deduction)
                            })
                        })
                        // frm.refresh_field('employees')
                        // frm.save()
                    }
                }
            }),

            // absent Deduction
            frappe.call({
                method: "stats.salary.calculate_absent_dedution",
                args: {
                    payroll_entry: frm.doc.name
                },
                callback: function (r) {
                    console.log(r.message, '--r.message')
                    let absent_deduction_list = r.message
                    if (absent_deduction_list.length > 0) {
                        absent_deduction_list.forEach((ele) => {
                            frm.doc.employees.forEach((row) => {
                                if (ele.employee == row.employee)
                                    frappe.model.set_value(row.doctype, row.name, "custom_absent_deduction", ele.absent_deduction)
                            })
                        })
                        // frm.refresh_field('employees')
                        // frm.save()
                    }
                }
            }),

            // Incomplete Monthly Mins Deduction
            frappe.call({
                method: "stats.salary.calculate_incomplete_monthly_mins_deduction",
                args: {
                    payroll_entry: frm.doc.name
                },
                callback: function (r) {
                    console.log(r.message, '--r.message')
                    let monthly_incomplete_mins_list = r.message
                    if (monthly_incomplete_mins_list.length > 0) {
                        monthly_incomplete_mins_list.forEach((ele) => {
                            frm.doc.employees.forEach((row) => {
                                if (ele.employee == row.employee)
                                    frappe.model.set_value(row.doctype, row.name, "custom_incomplete_monthly_mins_deduction", ele.incomplete_mins_deduction)
                            })
                        })
                        // frm.refresh_field('employees')
                        // frm.save()
                    }
                }
            })

            setTimeout(() => {
                frm.refresh_field('employees')
                frm.save()
            }, 2000);

            
        }
    }
})