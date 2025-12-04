# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import calendar
from frappe import _

month_number_mapping = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }

def execute(filters):
    if not filters: filters = {}

    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data

def get_columns(filters):

    # Employee Details Columns
    columns = [
        {
            'fieldname' : 'employee_id',
            'fieldtype' : 'Link',
            'label' : _('Employee ID'),
            'options' : 'Employee',
            'width' : 130
        },
        {
            'fieldname' : 'first_name',
            'fieldtype' : 'Data',
            'label' : _('First Name'),
            'width' : 130
        },
        {
            'fieldname' : 'idresidency_number',
            'fieldtype' : 'Data',
            'label' : _('ID/Residency Number'),
            'width' : 130
        },
        {
            'fieldname' : 'section',
            'fieldtype' : 'Link',
            'label' : _('Section'),
            'options' : 'Section ST',
            'width' : 130
        },
        {
            'fieldname' : 'main_department',
            'fieldtype' : 'Link',
            'label' : _('Main Department'),
            'options' : 'Department',
            'width' : 130
        },
        {
            'fieldname' : 'sub_department',
            'fieldtype' : 'Data',
            'label' : _('Sub Department'),
            'width' : 130
        },
    ]

    # Columns Of Selected Months From Filters
    current_month = month_number_mapping[filters.get('month')]
    current_year = frappe.utils.getdate().year
    firstday, lastday = calendar.monthrange(current_year, current_month)

    for i in range(1, lastday + 1):
        date = frappe.utils.getdate(f"{current_year}-{current_month}-{i}").strftime('%d')
        day = frappe.utils.get_weekday(frappe.utils.getdate(f"{current_year}-{current_month}-{i}"))

        column = {
            'fieldname' : f'{date}_{day}',
            'fieldtype' : 'Data',
            'label' : _(f'{date} {day}'),
            'width' : 130
        }

        columns.append(column)

    # Total Calculations Columns
    columns.extend([
        {
            'fieldname' : 'total_no_of_minutes_delay',
            'fieldtype' : 'Float',
            'label' : _('Total No Of Minutes Delay'),
            'width' : 130
        },
        {
            'fieldname' : 'total_no_of_hours',
            'fieldtype' : 'Data',
            'label' : _('Total No Of Hours'),
            'width' : 130
        },
        {
            'fieldname' : 'total_no_of_delay_days',
            'fieldtype' : 'Float',
            'label' : _('Total No Of Delay Days'),
            'width' : 130
        },
    ])

    return columns

def get_conditions(filters):
    conditions = {}
    for key, value in filters.items():
        if filters.get(key) and key != 'month':
            conditions[key] = value
    return conditions

def get_data(filters):
    conditions = get_conditions(filters)
    data = []
    
    # Employee Details
    employee_details = frappe.db.get_all(
        doctype = 'Employee',
        filters = conditions,
        fields = ['name', 'first_name', 'custom_idresidency_number', 'custom_section', 'department', 'custom_sub_department', 'holiday_list'],
        order_by = 'name'
    )
    
    if employee_details != None:
        for employee in employee_details:
            row = frappe._dict({
                'employee_id' : employee.name,
                'first_name'  : employee.first_name,
                'idresidency_number' : employee.custom_idresidency_number,
                'section' : employee.custom_section,
                'main_department' : employee.department,
                'sub_department' : employee.custom_sub_department,
            })

            # Employee Attendance Details
            current_month = month_number_mapping[filters.get('month')]
            current_year = frappe.utils.getdate().year
            firstday, lastday = calendar.monthrange(current_year, current_month)

            total_delay_minutes = 0
            total_delay_days = 0

            for i in range(1, lastday + 1):
                date = frappe.utils.getdate(f"{current_year}-{current_month}-{i}")
                delay_minutes = 0
                
                # Check For Weekend Or General Holiday
                if employee.holiday_list != None:
                    weekoff_holidays = frappe.db.get_all("Holiday", filters = {'parent': employee.holiday_list, 'weekly_off' : 1}, pluck ='holiday_date')
                    general_holidays = frappe.db.get_all("Holiday", filters = {'parent': employee.holiday_list, 'weekly_off' : 0}, pluck ='holiday_date')
                    if date in weekoff_holidays:
                        delay_minutes = "Weekend"
                    elif date in general_holidays:
                        desc = frappe.db.sql(f"SELECT th.description FROM tabHoliday th WHERE th.holiday_date = '{date}' AND th.weekly_off = 0", as_dict = 1)
                        delay_minutes = desc[0].description

                    
                elif employee.holiday_list == None:
                    holiday_list = frappe.db.get_value(
                        doctype = "Company",
                        filters = {"name" : frappe.defaults.get_user_default("company")},
                        fieldname = ['default_holiday_list']
                    )

                    weekoff_holidays = frappe.db.get_all("Holiday", filters = {'parent': holiday_list, 'weekly_off' : 1}, pluck ='holiday_date')
                    general_holidays = frappe.db.get_all("Holiday", filters = {'parent': holiday_list, 'weekly_off' : 0}, pluck ='holiday_date')
                    if date in weekoff_holidays:
                        delay_minutes = "Weekend"
                    elif date in general_holidays:
                        desc = frappe.db.sql(f"SELECT th.description FROM tabHoliday th WHERE th.holiday_date = '{date}' AND th.weekly_off = 0", as_dict = 1)
                        delay_minutes = desc[0].description
                
                # If not Weekend Or Holiday Then Check For Late Entry
                if delay_minutes == 0:
                    delay_details = frappe.db.sql(
                        f'''
                        SELECT 
                            ta.custom_actual_delay_minutes   
                        FROM 
                            tabAttendance ta
                        WHERE 
                            ta.attendance_date = '{date}' AND ta.employee = '{employee.name}' AND ta.late_entry = '1';
                        ''',
                    as_dict = 1, debug = 1)

                    if delay_details != []:
                        delay_minutes = delay_details[0].custom_actual_delay_minutes
                        total_delay_minutes = total_delay_minutes + delay_minutes
                        total_delay_days = total_delay_days + 1
                    else:  
                        delay_minutes = 0

                day_string = date.strftime('%d')
                date_string = '{current_year}-{current_month}-{i}'.format(current_year=current_year, current_month=current_month, i=i)
                weekday = frappe.utils.get_weekday(frappe.utils.getdate(date_string))

                field_name = "{0}_{1}".format(day_string, weekday)
                row['{0}'.format(field_name)] = delay_minutes
           
            total_seconds = float(total_delay_minutes) * 60
            row.update({
                'total_no_of_minutes_delay' : total_delay_minutes,
                'total_no_of_hours' : frappe.utils.format_duration(total_seconds) if total_seconds > 0 else '0s',
                'total_no_of_delay_days' : total_delay_days
            })


            data.append(row)

    return data