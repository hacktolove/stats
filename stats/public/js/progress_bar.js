$(document).on("form-refresh", function (event, frm) {
    // console.log("========================================progress_bar==========================", frm.doc.doctype)
    if (frappe.meta.has_field(frm.doc.doctype, "progress_bar") && frappe.meta.has_field(frm.doc.doctype, "workflow_state") ) {
        // console.log("--------has field-----------")
        if (
            frm.fields_dict["progress_bar"] &&
            frm.is_new() == undefined &&
            frm.doc.__onload && "workflow_progressbar_html" in frm.doc.__onload
        ) {
            console.log("Inside IFFF")
            frm.set_df_property('progress_bar', 'options', frm.doc.__onload.workflow_progressbar_html)
            frm.refresh_field('progress_bar')
        } else {
            console.log("Inside ELSEEEE")
            frm.set_df_property('progress_bar', 'options', "<div><div>")
            frm.refresh_field('progress_bar')
        }
    }
});