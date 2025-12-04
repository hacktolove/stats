frappe.listview_settings['Evacuation of Party ST'] = {
    onload: function (listview) {
        console.log("---------listview---------")
        setTimeout(() => {
            console.log("hiding button")
            $(`button[data-label="Add Evacuation of Party ST"]`).hide()
        }, 200);
    }
}