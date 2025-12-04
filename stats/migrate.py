import frappe

def after_migrate():
    frappe.db.set_value('Report', 'Employee Daily Check in', 'prepared_report', 0)
    frappe.db.set_value('Report', 'Employee Absent Report', 'prepared_report', 0)
    frappe.db.set_value('Report', 'Employee Continuous Absent Report', 'prepared_report', 0)
    frappe.db.set_value('Report', 'General Attendance Report', 'prepared_report', 0)