// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt


frappe.query_reports["Employee Daily Check in"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label":__("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"read_only":1
		},
		{
			"fieldname": "main_department",
			"label":__("Main Department"),
			"fieldtype": "Link",
			"options": "Department",
			"read_only":1,
			"hidden": 1,
			// "default":"الإحصاءات المكانية وإحصاءات الموارد - GS"
		},
		{
			"fieldname": "sub_department",
			"label":__("Sub Department"),
			"fieldtype": "Link",
			"options": "Department",
			"read_only":1,
			"hidden": 1
		},
		{
			"fieldname": "from_date",
			"label":__("From Date"),
			"fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label":__("To Date"),
			"fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
			"reqd": 1
		}
	],
	onload: set_filter_based_on_logged_in_user
};

function set_filter_based_on_logged_in_user(frm) {
	user_id = frappe.session.user
	frappe.call({
		method: "stats.stats.report.employee_daily_check_in.employee_daily_check_in.get_emp_access",
		args: {
			user_id : user_id,
		},
		callback: function(r) {
			console.log(r.message,"---")
			if (r.message) {
				frappe.query_report.set_filter_value("employee", r.message[0]);
				frappe.query_report.set_filter_value("main_department", r.message[1]);
				frappe.query_report.set_filter_value("sub_department", r.message[2]);
			}
		}
	})

	// hide_details_button_for_users except attendance manager

	frappe.call({
		method: "stats.stats.report.employee_daily_check_in.employee_daily_check_in.get_attendance_manager_role",
		callback: function (r) {
			let attandance_role = r.message
			if (attandance_role && !frappe.user.has_role(attandance_role)) {
				$('.menu-btn-group').hide()
			}

			// if (user_id == "Administrator") {
			// 	frappe.db.get_doc('User', user_id)
			// 		.then(doc => {
			// 			if (doc.roles) {
			// 				let has_attandance_role = false
			// 				for (let i = 0; i < doc.roles.length; i++) {
			// 					if (doc.roles[i].role == attandance_role) {
			// 						has_attandance_role = true
			// 					}
			// 				}

			// 				if (has_attandance_role == false) {
			// 					$('.menu-btn-group').hide()
			// 				}
			// 			}
			// 		})
			// }
		}
	})
}