app_name = "stats"
app_title = "Stats"
app_publisher = "GreyCube Technologies"
app_description = "Customization for stats"
app_email = "admin@greycube.in"
app_license = "mit"
required_apps = ["frappe/hrms"]

# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "stats.bundle.css"
app_include_js = ["custom_logout.bundle.js","in_words.bundle.js", "/assets/stats/js/progress_bar.js", "/assets/stats/js/rejected_reason.js"]
# /assets/wati_whatsapp/js/wati_whatsapp.js

# include js, css files in header of web template
# web_include_css = "/assets/stats/css/stats.css"
# web_include_js = "/assets/stats/js/stats.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "stats/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

page_js = {
    "user-profile" : "/public/js/user-profile.js"
}

doctype_js = {"ToDo" : "public/js/todo.js",
              "Employee":"public/js/employee.js",
              "Company":"public/js/company.js",
              "Department":"public/js/department.js",
              "Designation":"public/js/designation.js",
              "Payroll Entry": "public/js/payroll_entry.js",
              "Material Request":"public/js/material_request.js",
              "Leave Application":"public/js/leave_application.js",
              "Purchase Order":"public/js/purchase_order.js",
              "Purchase Invoice":"public/js/purchase_invoice.js",
              "Leave Allocation":"public/js/leave_allocation.js",
              "Leave Type":"public/js/leave_type.js"
              }

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "stats/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
	"methods": "stats.hr_utils.get_employee_emails",
	# "filters": "stats.utils.jinja_filters"
}

# Installation
# ------------

# before_install = "stats.install.before_install"
# after_install = "stats.install.after_install"

after_migrate = "stats.migrate.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "stats.uninstall.before_uninstall"
# after_uninstall = "stats.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "stats.utils.before_app_install"
# after_app_install = "stats.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "stats.utils.before_app_uninstall"
# after_app_uninstall = "stats.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "stats.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "*": {
        "onload": "stats.api.progress_bar_html_onload"
    },
    "ToDo": {
		"validate":["stats.api.set_todo_status_in_onboarding_procedures",
                    "stats.api.set_employee_company_email",
                    "stats.api.create_new_user_using_company_email_in_employee"]
	},
    "Employee": {
        "validate":["stats.api.calculate_years_of_experience",
                     "stats.api.convert_gregorian_dob_in_hijri_dob",
                    "stats.api.set_employee_in_man_power_planning_for_job_no",
                    "stats.salary.create_resignation_addition_salary_for_employee",
                    "stats.api.set_gosi_deduction_type_in_employee",
                    # "stats.salary.create_new_gosi_based_salary_for_eligible_employee"
                    ]
	},
    "Leave Application": {
        "validate":["stats.api.check_leave_is_not_in_business_days",
                    "stats.api.validate_leave_types",
                    "stats.api.set_no_of_leaves_in_draft_application",
                    "stats.api.validate_deputy_employee_if_applicable",
                    "stats.api.validate_past_dates_in_leave_application"]
	},
    "Offer Term": {
        "validate":"stats.api.check_monthly_salary_component_offer_term"
    },
    "Salary Structure": {
        "on_submit":"stats.api.create_salary_structure_assignment"
    },
    "Designation": {
        "validate":"stats.api.validate_weight_and_set_degree_based_on_weight"
    },
    "Attendance": {
        "validate":"stats.api.calculate_working_minutes_based_on_permission_request_or_work_out_of_office",
        "on_update_after_submit":"stats.api.calculate_extra_working_hours",
        "on_submit":["stats.api.set_custom_attendance_type",
                     "stats.api.deduct_permission_balance_and_compensatory_balance_from_employee"]
    },
    "Employee Checkin": {
        "after_insert":"stats.api.set_last_sync_of_checkin_on_save_of_employee_checkin",
        "before_validate":["stats.api.set_log_type_based_on_device_id",
                            "stats.api.set_time_based_on_shift_time",
                            "stats.api.increase_one_hour_for_breast_feeding_request"]
    },
    "Payroll Entry": {
        "before_submit": ["stats.salary.create_additonal_salary_for_deduction",
                          "stats.salary.create_addtional_salary_for_new_joinee"]
    },
    "Material Request": {
        "validate":["stats.api.validate_request_classification",
                    "stats.api.validate_total_amount_of_payment_table"]
    },
    "Purchase Order": {
        "validate":"stats.api.fetch_values_from_material_request"
    },
    "Employee Grade": {
        "validate":["stats.salary.validate_salary_amount_in_grade",
                    "stats.api.validate_evaluation_weight"]
    },
    "Attendance Request": {
        "validate":["stats.api.set_work_from_home_days_in_attendance_request",
                    "stats.api.validate_max_allowed_wfh_per_month_and_max_allowed_employee_per_day",
                    "stats.api.validate_attendance_request_from_date"]
    },
}

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
        # at start of every year at 1:30 night
        "30 1 1 1 *": [
            "stats.api.set_no_of_business_trip_days_available_at_start_of_every_year",
            "stats.api.reset_yearly_personal_permission_balance_in_employee"
        ],
        # at start of every month at 1:30 night
        "30 1 1 * *" : [
            "stats.api.reset_monthly_personal_permission_balance_and_copy_existing_balance_to_previous_month_in_employee",
            "stats.api.reset_monthly_compensatory_balance_to_zero_and_copy_existing_balance_to_previous_month_in_employee"
        ],
        # at 5th of every month at 1:30 night
        "30 1 5 * *": [
            "stats.api.previous_month_permission_balance_and_compensatory_balance_set_to_zero"
        ],
        "30 1 1 * *": [
            "stats.api.set_years_of_experience_at_start_of_every_month",
		],
        # at 11:30 PM every day
        "30 23 * * *": [
            "stats.api.set_scholarship_status_closed",
            "stats.api.set_last_sync_of_checkin_in_all_shift_type"
        ],
        "30 1 15 1 *":[
            "stats.hr_utils.set_yearly_permission_balance_in_employee_profile"
        ],
        "0 7 * * *":[
            "stats.api.inactive_employee_and_user_day_after_relieving_date"
        ],
        # at 01:00 AM every day
        "0 1 * * *": [
            "stats.api.calculate_remaining_days_to_close_petty_cash_request",
            "stats.api.transfer_employee_based_on_employee_transfer_st",
            "stats.api.reset_education_allowance_balance_for_employee_dependants"
        ],
        #  at 2: 00 AM on the 1st July every year
        "0 2 1 7 *": [
            "stats.salary.create_new_gosi_based_salary_for_eligible_employee"
        ],
        # "*/5 * * * *": [
        #     "stats.salary.create_new_gosi_based_salary_for_eligible_employee"
        # ],
	},
    "daily": [
        # "stats.api.create_employee_evaluation_yearly_and_half_yearly",
        "stats.api.create_employee_evaluation_based_on_employee_contract"
    ]
}
# 	"all": [
# 		"stats.tasks.all"
# 	],
# 	"daily": [
# 		"stats.tasks.daily"
# 	],
# 	"hourly": [
# 		"stats.tasks.hourly"
# 	],
# 	"weekly": [
# 		"stats.tasks.weekly"
# 	],
# 	"monthly": [
# 		"stats.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "stats.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "stats.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "stats.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["stats.utils.before_request"]
# after_request = ["stats.utils.after_request"]

# Job Events
# ----------
# before_job = ["stats.utils.before_job"]
# after_job = ["stats.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

auth_hooks = ["stats.auth.validate_portal_user"]
# website_redirects = [
#  {"source": "/login", "target": "/redirect_to_portal_login"}
# ]
# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

