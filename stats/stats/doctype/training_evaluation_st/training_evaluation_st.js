// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Evaluation ST", {
	onload(frm) {
        const evaluate_fields = [
            "achieving_the_goals_of_the_program_training", "adapting_content_to_business_needs", "clarity_and_organization_of_scientific_material", "diversity_of_presentation_and_explanation_methods",
            "the_trainer_mastered_the_scientific_material", "delivery_and_communication_style", "ability_to_motivate_trainees", "effective_time_management",
            "organizing_the_workshop_and_the_schedule","suitability_of_the_workshop_location","support"
        ];
        const postfixes = ["ex", "vg", "go", "ac", "wk"];

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
    }
});

function make_read_only(frm, field_prefix, selected_field) {
    const postfixes = ["ex", "vg", "go", "ac", "wk"];
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