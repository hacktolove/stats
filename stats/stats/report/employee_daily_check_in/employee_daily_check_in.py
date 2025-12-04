# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.nestedset import get_descendants_of
from frappe.core.doctype.role.role import get_users

def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	columns = [
		{
			"fieldname": "employee",
			"fieldtype": "Link",
			"label": _("Employee ID"),
			"options": "Employee",
			"width": 540
		},
		{
			"fieldname": "log_type",
			"label":_("Log Type"),
			"fieldtype": "Select",
			"options": "IN\nOUT",
			"width": 200
		},
		{
			"fieldname": "physical_device_time",
			"fieldtype": "Datetime",
			"label": _("Physical Device Time"),
			"width": 300
		},
		{
			"fieldname": "main_department",
			"label":_("Main Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": 300
		},
		{
			"fieldname": "sub_department",
			"label":_("Sub Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": 300
		}
	]
	return columns

def get_data(filters):
	role = frappe.db.get_single_value("Stats Settings ST","attendance_hide_role")
	user_list = get_users(role)
	employee_list = []
	if len(user_list) > 0:
		for user in user_list:
			employee = frappe.db.exists("Employee",{"user_id":user})
			if employee:
				employee_list.append(employee)
	print(user_list, "-------------user_list")
	print(employee_list,"-----employee")
	if len(employee_list)>0:
		emp=tuple(employee_list) if len(employee_list)>1 else (employee_list[0],"")
	else:
		emp=("","")
	print(emp, type(emp), "+++++++++++++++++")
	print(filters,"--filters")
	conditions = get_conditions(filters)

	employee_checkin_list = frappe.db.sql("""
								SELECT
								e.name as employee,
								e.employee_name,
								e.department as main_department,
								e.custom_sub_department as sub_department,
								ec.log_type,
								ec.custom_physical_device_time as physical_device_time
							FROM
								`tabEmployee Checkin` as ec
							INNER JOIN `tabEmployee` as e ON
								e.name = ec.employee
							WHERE {0} and e.employee NOT IN {1}
					""".format(conditions,emp),as_dict=1)
	final_employee_checkin_data = []
	# print(employee_checkin_list,"------------employee_checkin_list")
	if len(employee_checkin_list)>0:
		for checkin in employee_checkin_list:
			if filters.get("main_department"):
				print("======MAIN",filters.get("main_department"))
				all_descendant_departments = get_descendants_of("Department", filters.get("main_department"),ignore_permissions=True)
				print(all_descendant_departments,"------------all_descendant_departments")
				if len(all_descendant_departments)>0:
					if checkin.sub_department in all_descendant_departments or checkin.main_department in all_descendant_departments:
						final_employee_checkin_data.append(checkin)
			elif filters.get("sub_department"):
				print("====== SUB" )
				if checkin.sub_department == filters.get("sub_department"):
					final_employee_checkin_data.append(checkin)
			elif filters.get("employee"):
				print("======EMPLOYEE")
				if checkin.employee == filters.get("employee"):
					final_employee_checkin_data.append(checkin)
			else:
				print("====ALL")
				final_employee_checkin_data.append(checkin)
		print(final_employee_checkin_data,"--------------------final")

	return final_employee_checkin_data

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " DATE(ec.time) between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))

	# if filters.get("employee"):
	# 	conditions += " and e.name = '{0}' ".format(filters.get("employee"))
	
	# if filters.get("main_department"):
	# 	conditions += " and e.department = '{0}' ".format(filters.get("main_department"))

	# if filters.get("sub_department"):
	# 	conditions += " and e.custom_sub_department = '{0}' ".format(filters.get("sub_department"))
	return conditions

@frappe.whitelist()
def get_emp_access(user_id):
	employee,main_department,sub_department=None,None,None
	
	user_roles = frappe.get_roles(frappe.session.user)
	print(user_roles,"===========user_roles")
	attendance_manager_role = frappe.db.get_single_value("Stats Settings ST","attendance_manager_role")
	if (user_id=="Administrator") or (attendance_manager_role in user_roles):
		print("IN IF")
		return employee,main_department,sub_department
	else :
		employee_id,employee_sub_department,department,is_manager=frappe.db.get_value('Employee', {'user_id': user_id}, ['name', 'custom_sub_department','department','custom_is_manager'])
		print(employee_id,"----------------employee_id")
		# if is_manager==1:
		# 	main_department=department
		# 	return employee,main_department,sub_department
		# elif is_manager==0:
		main_dep = frappe.db.get_value('Department', {'custom_main_department_manager': employee_id}, ['name'])
		print(main_dep,"----------------main_dep")
		if main_dep:
			print("IN CONDITION")
			main_department=main_dep
			return employee,main_department,sub_department
		else:
			direct_mananger_dep=frappe.db.get_value('Department', {'custom_direct_manager': employee_id}, ['name'])
			print(direct_mananger_dep,"----direct_mananger_dep------------------------------------------")
			if direct_mananger_dep!=None:
				sub_department=direct_mananger_dep
				return employee,main_department,sub_department
			else:
				employee=employee_id
				return employee,main_department,sub_department

@frappe.whitelist()
def get_attendance_manager_role():
    attendance_role = frappe.db.get_single_value('Stats Settings ST', 'attendance_manager_role')
    if attendance_role:
        return attendance_role
    else:
        frappe.throw(_("Attendance Manager Role not found in Stats Settings ST"))