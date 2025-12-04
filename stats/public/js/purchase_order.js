frappe.ui.form.on("Purchase Order", {
    onload(frm) {
        if (frm.is_new()){
        frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department', 'custom_sub_department'])
            .then(r => {
                let values = r.message;
                frm.set_value('custom_created_by', values.employee_name)
                frm.set_value('custom_main_department', values.department)
                frm.set_value('custom_sub_department', values.custom_sub_department)
            })
        }
    },

    refresh(frm) {
        if (frm.doc.docstatus == 1){
            frm.add_custom_button(__('PO Payment Schedule'),function () {
                frappe.model.open_mapped_doc({
                    method: "stats.api.create_po_payment_schedule",
                    frm: frm,
                });
            },__("Create"));
            
            frm.add_custom_button(__('Create Achievement Certificate'), () => create_achievement_certificate(frm),__("Create"));
        }
        
    },

    custom_supply_period_option(frm){
        calculate_contract_end_date(frm)
    },

    custom_supply_period(frm){
        calculate_contract_end_date(frm)
    },

    custom_contract_start_date(frm){
        calculate_contract_end_date(frm)
        calculate_contract_period(frm)
    },

    custom_contract_end_date(frm){
        calculate_contract_period(frm)
    }
})

let calculate_contract_end_date = function(frm){

    if (frm.doc.custom_supply_period){
        let supply_period = frm.doc.custom_supply_period
        if (frm.doc.custom_contract_start_date){
            let statr_date = frm.doc.custom_contract_start_date

            if (frm.doc.custom_supply_period_option == "Day"){
                let end_date = frappe.datetime.add_days(statr_date, supply_period)
                frm.set_value("custom_contract_end_date",end_date)
            }

            if (frm.doc.custom_supply_period_option == "Week"){
                let week_days = supply_period * 7
                let end_date = frappe.datetime.add_days(statr_date, week_days)
                frm.set_value("custom_contract_end_date",end_date)
            }

            if (frm.doc.custom_supply_period_option == "Month"){
                let end_date = frappe.datetime.add_months(statr_date, supply_period)
                frm.set_value("custom_contract_end_date",end_date)
            }

            if (frm.doc.custom_supply_period_option == "Year"){
                let end_date = frappe.datetime.add_months(statr_date, supply_period*12)
                frm.set_value("custom_contract_end_date",end_date)
            }
        }
    }
}

let calculate_contract_period = function(frm){
    if (frm.doc.custom_contract_start_date && frm.doc.custom_contract_end_date){
        let start_date = frm.doc.custom_contract_start_date
        let end_date = frm.doc.custom_contract_end_date
        let period = frappe.datetime.get_diff(end_date, start_date)
        frm.set_value("custom_contract_period",period)
        console.log(frm.doc.custom_contract_period)
    }
}

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