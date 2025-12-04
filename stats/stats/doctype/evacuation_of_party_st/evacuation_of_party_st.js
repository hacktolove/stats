// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Evacuation of Party ST", {
	refresh(frm) {
        hide_add_remove_buttons(frm)

        // only Department Manager can change the status of First Level Task
        if(frappe.user.has_role("Department Manager")) {
            console.log("OK")
            frm.set_df_property("fl_status", "read_only", 0)
        }
        else{
            frm.set_df_property("fl_status", "read_only", 1)
        }

        // only HR Operation Manager can change the status of Third Level Task
        if(frappe.user.has_role("HR Operation Manager")) {
            frm.fields_dict.evacuation_third_level_tasks.grid.update_docfield_property('status', 'read_only', 0);
        }
        else{
            frm.fields_dict.evacuation_third_level_tasks.grid.update_docfield_property('status', 'read_only', 1);
        }
        remove_readolny_for_logged_in_user(frm)
	},

    onload(frm) {
        fetch_terms_and_conditions(frm)
    },

    fl_status(frm){
        hide_add_remove_buttons(frm)
    },
    onload_post_render(frm){
     allow_admin_to_change_user(frm)   
    }

    // add_evacuation_third_level_tasks(frm) {
    //     frm.call("add_evacuation_third_level_tasks")
    // },
});

frappe.ui.form.on("Evacuation Task And Approval ST", {
    status(frm, cdt, cdn) {
        frm.call("check_second_level_completed")
    },

    evacuation_second_level_tasks_add(frm) {
        console.log("Adding Second Level Tasks")
        frm.reload_doc()
        frappe.throw(__("Second Level Tasks can not be added manually"));
    },

    evacuation_second_level_tasks_remove(frm) {
        console.log("Adding Second Level Tasks")
        frm.reload_doc()
        frappe.throw(__("Second Level Tasks can not be deleted manually"));
    },

    evacuation_third_level_tasks_add(frm) {
        console.log("Adding Third Level Tasks")
        frm.reload_doc()
        frappe.throw(__("Third Level Tasks can not be added manually"));
    },

    evacuation_third_level_tasks_remove(frm) {
        console.log("Adding Third Level Tasks")
        frm.reload_doc()
        frappe.throw(__("Third Level Tasks can not be deleted manually"));
    }
})

let fetch_terms_and_conditions = function(frm) {
    if ( frm.doc.docstatus == 0 )
    frappe.db.get_single_value("Stats Settings ST","evacuation_of_party_terms")
    .then(evacuation_of_party_terms => {
        if ( evacuation_of_party_terms && evacuation_of_party_terms.length > 0 ) {
            frm.set_value("terms_and_conditions",evacuation_of_party_terms)
        } else {
            frappe.throw(__("Please set Evacuation of Party Terms in Stats Settings ST"))
        }

    })
}

let remove_readolny_for_logged_in_user = function(frm) {
    if (frm.doc.evacuation_second_level_tasks.length > 0) {
        frm.doc.evacuation_second_level_tasks.forEach(element => {
            if ( element.in_charge_person == frappe.session.user ) {
                frm.fields_dict.evacuation_second_level_tasks.grid.grid_rows[element.idx-1].docfields[4].read_only=0
                frm.fields_dict.evacuation_second_level_tasks.grid.grid_rows[element.idx-1].docfields[5].read_only=0
            }
        });
    }

    if (frm.doc.evacuation_third_level_tasks.length > 0) {
        frm.doc.evacuation_third_level_tasks.forEach(element => {
            if ( element.in_charge_person == frappe.session.user ) {
                frm.fields_dict.evacuation_third_level_tasks.grid.grid_rows[element.idx-1].docfields[4].read_only=0
                frm.fields_dict.evacuation_third_level_tasks.grid.grid_rows[element.idx-1].docfields[5].read_only=0
            }
        });
    }
}

let hide_add_remove_buttons = function(frm) {
    setTimeout(() => {
        $("button.grid-add-row").hide()
        $("button.grid-remove-rows").hide()   
    }, 500);
}

let allow_admin_to_change_user = function (frm) {
    if (frappe.session.user == "Administrator") {
        if (frm.doc.evacuation_second_level_tasks.length > 0) {
            frm.doc.evacuation_second_level_tasks.forEach(element => {
                frm.fields_dict.evacuation_second_level_tasks.grid.grid_rows[element.idx - 1].docfields[1].read_only = 0
            });
        }

        if (frm.doc.evacuation_third_level_tasks.length > 0) {
            frm.doc.evacuation_third_level_tasks.forEach(element => {
                frm.fields_dict.evacuation_third_level_tasks.grid.grid_rows[element.idx - 1].docfields[1].read_only = 0
            });
        }
    }
}