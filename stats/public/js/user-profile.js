frappe.pages["user-profile"].on_page_show = function (wrapper) {
    setTimeout(() => {
        // $('button[data-label="Change User"]').hide()
        $('div.standard-actions button.btn-secondary.btn-default.btn-sm').hide()
    }, 250);
};