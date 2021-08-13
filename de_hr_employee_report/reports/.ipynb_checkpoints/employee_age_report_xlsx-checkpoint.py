import xlwt
from odoo import models
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class EmployeeAgeReport(models.AbstractModel):
    _name = 'report.de_hr_employee_report.employee_age_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Employee Age Report XLSX'
    
    def generate_xlsx_report(self, workbook, data, lines):
        
        type_employee = self.env['employee.type'].search([('id', 'in', data['employee_type_ids'])])
        employee_type = []
        for rec in type_employee:
            employee_type.append(rec.name)
        
        em_type = ','.join(employee_type)
        grade_type = self.env['grade.type'].search([('id', 'in', data['grade_type_ids'])])
        g_type = []
        for rec in grade_type:
            g_type.append(rec.name)
        
        gr_type = ','.join(g_type)
        location = self.env['hr.work.location'].search([('id', 'in', data['location_ids'])])
        locations = []
        for rec in location:
            locations.append(rec.name)
        
        loc = ','.join(locations)
        department = self.env['hr.department'].search([('id', 'in', data['department_ids'])])
        departments = []
        for rec in department:
            departments.append(rec.name)
        #raise UserError(departments)
        dep = ','.join(departments)
        age_from = data['age_from']
        age_to = data['age_to']
        
        format1 = workbook.add_format({'font_size': '14', 'align': 'vcenter', 'bold': True})
        sheet = workbook.add_worksheet('Cost Center Wise Report')
        
        sheet.write(3, 0, 'Age From', format1)
        sheet.write(3, 1, age_from, format1)
        sheet.write(3, 3, 'Emp Type', format1)
        sheet.write(3, 4, em_type, format1)
        sheet.write(3, 6, 'Department', format1)
        sheet.write(3, 7, dep, format1)
        sheet.write(4, 0, 'Age To', format1)
        sheet.write(4, 1, age_to, format1)
        sheet.write(4, 3, 'Grade Type', format1)
        sheet.write(4, 4, gr_type, format1)
        sheet.write(4, 6, 'Location', format1)
        sheet.write(4, 7, loc, format1)
        
        
        sheet.write(6, 0, 'Sr #', format1)
        sheet.write(6, 1, 'Emp Code', format1)
        sheet.write(6, 2, 'Name', format1)
        sheet.write(6, 3, 'Department', format1)
        sheet.write(6, 4, 'Employee Type', format1)
        sheet.write(6, 5, 'Grade Type', format1)
        sheet.write(6, 6, 'DOB', format1)
        sheet.write(6, 7, 'Age(YY-MM-DD)', format1)
        sheet.write(6, 8, 'Years', format1)
        sheet.write(6, 9, 'Months', format1)
        sheet.write(6, 10, 'Days', format1)
        
        
        format2 = workbook.add_format({'font_size': '12', 'align': 'vcenter'})
        row = 7
        sheet.set_column(row, 0, 50)
        sheet.set_column(row, 1, 25)
        sheet.set_column(row, 2, 20)
        sheet.set_column(row, 3, 20)
        sheet.set_column(row, 4, 20)
        sheet.set_column(row, 5, 20)
        sheet.set_column(row, 6, 20)
        sheet.set_column(row, 7, 20)
        sheet.set_column(row, 8, 20)
        sheet.set_column(row, 9, 20)
        sheet.set_column(row, 10, 20)
        
        
        
        employees = []
        if employee_type and grade_type and location and department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.grade_type', 'in', g_type),
                                                              ('employee_id.work_location_id', 'in',locations),
                                                              ('employee_id.department_id', 'in',
                                                               departments)])
            
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
                    
                    
                    #raise UserError(name)
            
        elif employee_type and grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type),
                                                              ('employee_id.grade_type', '=', grade_type)])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
                    
        elif employee_type and location:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type),
                                                              ('employee_id.work_location_id', '=',location)])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
                    
        elif employee_type and department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type),
                                                              ('employee_id.department_id', '=',
                                                               department)])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
                    
        elif employee_type and grade_type and location:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type),
                                                              ('employee_id.grade_type', '=', grade_type),
                                                              ('employee_id.work_location_id', '=',location)
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
                    
        elif employee_type and grade_type and department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type),
                                                              ('employee_id.grade_type', '=', grade_type),
                                                              ('employee_id.department_id', '=',
                                                               department)
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
                    
        elif employee_type and location and department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type),
                                                              ('employee_id.work_location_id', '=',location),
                                                              ('employee_id.department_id', '=',
                                                               department)
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
        
        elif grade_type and location and department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.grade_type', '=', grade_type),
                                                              ('employee_id.work_location_id', '=',location),
                                                              ('employee_id.department_id', '=',
                                                               department)
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
        
        
        
        elif location and department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.work_location_id', '=',location),
                                                              ('employee_id.department_id', '=',
                                                               department)
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
        
        elif location and grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.work_location_id', '=',location),
                                                              ('employee_id.grade_type', '=', grade_type)
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
        
        elif department and grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.grade_type', '=', grade_type),
                                                              ('employee_id.department_id', '=',
                                                               department)
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
        elif department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.department_id', '=',
                                                               department)
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
        
        elif grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.grade_type', '=', grade_type)
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
        
        elif location:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.work_location_id', '=',location)
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
        
        elif employee_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type)
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
        
        else:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open')
                                                              ])
            count = 1
            for contract in active_contract:
                birth_date = contract.employee_id.birthday
                parse_birth_date = birth_date.strftime("%Y-%m-%d")
                birth_year = birth_date.year
                birth_month = birth_date.month
                birth_day = birth_date.day
                
                today = date.today()
                t = today.strftime("%Y-%m-%d")
                today_year = today.year
                today_month = today.month
                today_day = today.day
                #raise UserError(today_year)
                employee_age = today_year - birth_year
                years = relativedelta(date.today(),birth_date).years
                months = relativedelta(date.today(),birth_date).months
                days = relativedelta(date.today(),birth_date).days
                age_details = ''
                age_details = str(years)+'Y-'+str(months)+'M-'+str(days)+'D'
                
                total_days = (today - birth_date).days
                total_months = months + (12*years)
                total_years = years
                #raise UserError(parse_birth_date)
                #raise UserError(total_months)
                
                if (employee_age >= age_from) and (employee_age <= age_to):
                    employee_dict = {}
                    sr_no = count
                    emp_code = contract.employee_id.emp_number
                    name = contract.employee_id.name
                    dep_name = contract.employee_id.department_id.name
                    emp_type = contract.employee_id.emp_type
                    g_type = contract.employee_id.grade_type.name
                    dob = parse_birth_date
                    age = age_details
                    year = total_years
                    month = total_months
                    day = total_days
                    count = count + 1

                    employee_dict['sr_no'] = sr_no
                    employee_dict['emp_code'] = emp_code
                    employee_dict['name'] = name
                    employee_dict['dep_name'] = dep_name
                    employee_dict['emp_type'] = emp_type
                    employee_dict['g_type'] = g_type
                    employee_dict['dob'] = dob
                    employee_dict['age'] = age
                    employee_dict['year'] = year
                    employee_dict['month'] = month
                    employee_dict['date'] = day
                    employees.append(employee_dict)
        
        for employee in employees:
            
            sheet.write(row, 0, employee['sr_no'], format2)
            sheet.write(row, 1, employee['emp_code'], format2)
            sheet.write(row, 2, employee['name'], format2)
            sheet.write(row, 3, employee['dep_name'], format2)
            sheet.write(row, 4, employee['emp_type'], format2)
            sheet.write(row, 5, employee['g_type'], format2)
            sheet.write(row, 6, employee['dob'], format2)
            sheet.write(row, 7, employee['age'], format2)
            sheet.write(row, 8, employee['year'], format2)
            sheet.write(row, 9, employee['month'], format2)
            sheet.write(row, 10, employee['date'], format2)
            
            row = row + 1
            
            
            