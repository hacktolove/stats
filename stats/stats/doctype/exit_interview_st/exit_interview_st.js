// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Exit Interview ST", {
	onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'employee_name')
            .then(r => {
                let values = r.message;
                frm.set_value('interview_done_by', values.employee_name)
            })
        }  

        const evaluate_fields = [
            "work_environment", "salary", "treatment", "work_training",
            "team_work", "communication", "supervising", "respect"
        ];
        const postfixes = ["ex", "vg", "go", "wk", "vwk"];

        evaluate_fields.forEach(prefix => {
            postfixes.forEach(suffix => {
                const evaluate_fieldname = `${prefix}_${suffix}`;
                if (frm.doc.docstatus == 0 && frm.doc[evaluate_fieldname] == 1) {
                    make_read_only(frm, prefix, evaluate_fieldname);
                }
                frm.fields_dict[evaluate_fieldname].df.onchange = () => {
                    make_read_only(frm, prefix, evaluate_fieldname);
                }
            });
        });
    },

});

function make_read_only(frm, field_prefix, selected_field) {
    const postfixes = ["ex", "vg", "go", "wk", "vwk"];
    postfixes.forEach(postfix => {
        const evaluate_fieldname = `${field_prefix}_${postfix}`;
        if (evaluate_fieldname !== selected_field && frm.doc[selected_field] == 1) {
            frm.set_value(evaluate_fieldname, 0);
            frm.set_df_property(evaluate_fieldname, 'read_only', 1);
        } else {
            frm.set_df_property(evaluate_fieldname, 'read_only', 0);
        }
    });
}