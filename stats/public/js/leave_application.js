frappe.ui.form.on("Leave Application", {
	set_leave_type: function (frm) {
		// code from hrms app except stats filter 2 lines
		if (frm.doc.employee) {
			frappe.call({
				method: "hrms.hr.doctype.leave_application.leave_application.get_leave_details",
				async: false,
				args: {
					employee: frm.doc.employee,
					date: frm.doc.from_date || frm.doc.posting_date,
				},
				callback: function (r) {
					if (!r.exc && r.message["leave_allocation"]) {
						leave_details = r.message["leave_allocation"];
					}
					lwps = r.message["lwps"];
				},
			});

			$("div").remove(".form-dashboard-section.custom");

			frm.dashboard.add_section(
				frappe.render_template("leave_application_dashboard", {
					data: leave_details,
				}),
				__("Allocated Leaves"),
			);
			frm.dashboard.show();

			let allowed_leave_types = Object.keys(leave_details);
			// lwps should be allowed for selection as they don't have any allocation
			allowed_leave_types = allowed_leave_types.concat(lwps);
			console.log("allowed_leave_types", allowed_leave_types)

			frm.set_query("leave_type", function () {
				return {
					filters: [
						["leave_type_name", "in", allowed_leave_types],
						["custom_based_on_leave_request", "!=", 1],      // stats filter
						["custom_once_in_company_life", "!=", 1]],		// stats filter
				};
			});
		}
	},

	refresh: function (frm) {

		frm.trigger("set_leave_type")
		if (frm.doc.status == 'Approved' && frm.doc.docstatus == 1) {
			frm.add_custom_button(
				__("Leave Change Request"),
				function () {
					frappe.model.open_mapped_doc({
						method: "stats.api.make_leave_application_change_request",
						frm: frm,
					});
				});
		}
	},

	onload: function(frm){
		frm.set_query("custom_deputy_employee", function () {
                return {
                    query: "stats.api.get_deputy_employee_list",
                    filters: {
                        employee: frm.doc.employee
                    }
                };
        });
	},
	employee: function (frm) {
		frm.trigger("set_leave_type")

		frappe.db.get_value('Employee', frm.doc.employee, 'custom_country')
			.then(r => {
				console.log(r.message.custom_country, "=========custom_country")
				if (r.message.custom_country == "Saudi Arabia") {
					frm.set_df_property('custom_exit_entry_required', 'hidden', 0)
					frm.set_df_property('custom_ticket_required', 'hidden', 1)
				}
				else if (r.message.custom_country) {
					frm.set_df_property('custom_exit_entry_required', 'hidden', 1)
					frm.set_df_property('custom_ticket_required', 'hidden', 0)
				}
				else {
					frm.set_df_property('custom_exit_entry_required', 'hidden', 1)
					frm.set_df_property('custom_ticket_required', 'hidden', 1)
				}


			})
	},
	leave_type: function (frm) {
		frm.trigger("set_leave_type")
		// if (frm.doc.leave_type) {
		// 	frappe.call({
		// 		method: "stats.api.set_no_of_leaves_in_draft_application",
		// 		args: {
		// 			leave_type: frm.doc.leave_type,
		// 			employee: frm.doc.employee,
		// 		},
		// 		callback: function (r) {
		// 			if (r.message) {
		// 				frm.set_value("custom_no_of_leaves_in_draft_application", r.message);
		// 			}
		// 		},
		// 	});
		// }
	},
	from_date: function (frm) {
		frm.trigger("set_leave_type")
	},
	to_date: function (frm) {
		frm.trigger("set_leave_type")
	},
})