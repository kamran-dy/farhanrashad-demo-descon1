# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date


class EmployeeInformationPDF(models.AbstractModel):
    _name = 'report.de_hr_employee_report.employee_information_pdf'
    _description = 'Employee Information PDF Report'

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
        
        department = self.env['hr.department'].search([('id', 'in', data['department_ids'])])
        departments = []
        for rec in department:
            departments.append(rec.name)
        #raise UserError(departments)
        dep = ','.join(departments)
        
        
        employees = []
        if employee_type and grade_type and department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.grade_type', 'in', g_type),
                                                              ('employee_id.department_id', 'in',
                                                               departments)])
            
            
        elif employee_type and grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type),
                                                              ('employee_id.grade_type', '=', grade_type)])
                     
        elif employee_type and department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type),
                                                              ('employee_id.department_id', '=',
                                                               department)])
        
        elif department and grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.grade_type', '=', grade_type),
                                                              ('employee_id.department_id', '=',
                                                               department)
                                                              ])
        elif department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.department_id', '=',
                                                               department)
                                                              ])
        elif grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.grade_type', '=', grade_type)
                                                              ])
        elif employee_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type)
                                                              ])
        
        else:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open')
                                                              ])
            
                    
        return {
            'doc_ids': self.ids,
            'doc_model': 'employee.information',
            'data': data,
            'employee_type': em_type,
            'grade_type': gr_type,
            'department': dep,
            'active_contract': active_contract,
            'email':data['email'],
            'mobile':data['mobile'],
            'address':data['address'],
            'religion':data['religion'],
            'cnic':data['cnic'],
            'blood_group':data['blood_group'],
            'bank_account_number':data['bank_account_number'],
            'card_no':data['card_no'],
            'emergency_contact':data['emergency_contact'],
            'assets':data['assets'],
            'dependent':data['dependent'],
            'pfund':data['pfund'],
            'eobi_number':data['eobi_number'],
            'gratuity':data['gratuity'],
            'contract_details':data['contract_details'],
            'employees':employees,
        }
