# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import date, datetime, timedelta
from itertools import groupby


class EmployeeExperiencePDF(models.AbstractModel):
    _name = 'report.de_hr_employee_report.employee_experience_pdf'
    _description = 'Employee Experience PDF Report'

    def _get_report_values(self, docids, data):
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
        
        employees = []
        
        if employee_type and grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.grade_type', 'in', g_type)])
            count = 1
            for contract in active_contract:
                employee_dict = dict()
                sr_no = count
                e_type = contract.employee_id.emp_type
                company = contract.employee_id.company_id.name
                emp_code =  contract.employee_id.emp_number
                name = contract.employee_id.name
                designation = contract.employee_id.job_id.name
                grade = contract.employee_id.grade_designation.name
                department = contract.employee_id.department_id.name
                doj = contract.employee_id.date
                years = relativedelta(date.today(),doj).years
                months = relativedelta(date.today(),doj).months
                days = relativedelta(date.today(),doj).days
                
                count = count + 1
                
                employee_dict['sr_no'] = sr_no
                employee_dict['company'] = company
                employee_dict['emp_code'] = emp_code
                employee_dict['emp_type'] = e_type
                employee_dict['name'] = name
                employee_dict['designation'] = designation
                employee_dict['grade'] = grade
                employee_dict['department'] = department
                employee_dict['doj'] = doj
                employee_dict['years'] = years
                employee_dict['months'] = months
                employee_dict['days'] = days
                employees.append(employee_dict)
        
        elif employee_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type)
                                                            ])
            count = 1
            for contract in active_contract:
                employee_dict = dict()
                sr_no = count
                e_type = contract.employee_id.emp_type
                company = contract.employee_id.company_id.name
                emp_code =  contract.employee_id.emp_number
                name = contract.employee_id.name
                designation = contract.employee_id.job_id.name
                grade = contract.employee_id.grade_designation.name
                department = contract.employee_id.department_id.name
                doj = contract.employee_id.date
                years = relativedelta(date.today(),doj).years
                months = relativedelta(date.today(),doj).months
                days = relativedelta(date.today(),doj).days
                
                count = count + 1
                
                employee_dict['sr_no'] = sr_no
                employee_dict['company'] = company
                employee_dict['emp_code'] = emp_code
                employee_dict['emp_type'] = e_type
                employee_dict['name'] = name
                employee_dict['designation'] = designation
                employee_dict['grade'] = grade
                employee_dict['department'] = department
                employee_dict['doj'] = doj
                employee_dict['years'] = years
                employee_dict['months'] = months
                employee_dict['days'] = days
                employees.append(employee_dict)
        
        elif grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.grade_type', 'in', g_type)
                                                            ])
            count = 1
            for contract in active_contract:
                employee_dict = dict()
                sr_no = count
                e_type = contract.employee_id.emp_type
                company = contract.employee_id.company_id.name
                emp_code =  contract.employee_id.emp_number
                name = contract.employee_id.name
                designation = contract.employee_id.job_id.name
                grade = contract.employee_id.grade_designation.name
                department = contract.employee_id.department_id.name
                doj = contract.employee_id.date
                years = relativedelta(date.today(),doj).years
                months = relativedelta(date.today(),doj).months
                days = relativedelta(date.today(),doj).days
                
                count = count + 1
                
                employee_dict['sr_no'] = sr_no
                employee_dict['company'] = company
                employee_dict['emp_code'] = emp_code
                employee_dict['emp_type'] = e_type
                employee_dict['name'] = name
                employee_dict['designation'] = designation
                employee_dict['grade'] = grade
                employee_dict['department'] = department
                employee_dict['doj'] = doj
                employee_dict['years'] = years
                employee_dict['months'] = months
                employee_dict['days'] = days
                employees.append(employee_dict)
        
        employees = sorted(employees, key = lambda i: i['emp_code'])
        
        
                    
        return {
            'doc_ids': self.ids,
            'doc_model': 'employee.dob',
            'data': data,
            'active_contract': active_contract,
            'employees':employees
        }
