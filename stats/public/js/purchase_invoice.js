frappe.ui.form.on("Purchase Invoice", { 
    refresh(frm) {
        if (frm.doc.docstatus == 1){
        frm.add_custom_button(__('Create Achievement Certificate'), () => create_achievement_certificate(frm));
        }
    }
});

let create_achievement_certificate = function (frm) {
    frappe.call({
        method: "stats.api.create_achievement_certificate",
        args: {
            doctype: frm.doc.doctype,
            doc: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                let certificate_name = r.message
                frappe.open_in_new_tab = true;
                frappe.set_route("Form", "Achievement Certificate ST", certificate_name);
            }
        }
    });
}