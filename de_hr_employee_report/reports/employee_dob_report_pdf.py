# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date


class EmployeeDOBPDF(models.AbstractModel):
    _name = 'report.de_hr_employee_report.employee_dob_pdf'
    _description = 'Employee DOB PDF Report'

    def _get_report_values(self, docids, data):
        
        todays_date = date.today()
        todays_year = todays_date.year
        company_ids = self.env['res.company'].search([('id', 'in', data['company_ids'])])
        companyids = []
        for rec in company_ids:
            companyids.append(rec.name)
        #raise UserError(companyids)
        employees = []
        if company_ids:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.company_id', 'in', companyids),
                                                            ])
            for contract in active_contract:
                employee_dict = {}
                emp_code =  contract.employee_id.emp_number
                name = contract.employee_id.name
                department = contract.employee_id.department_id.name
                doj = contract.employee_id.date.strftime("%d-%m-%Y")
                dob = contract.employee_id.birthday.strftime("%d-%m-%y")
                birthday = contract.employee_id.birthday.strftime("%d-%m-{}".format(todays_year))
                company = contract.employee_id.company_id.name
                #raise UserError(emp_code)
                
                employee_dict['emp_code'] = emp_code
                employee_dict['name'] = name
                employee_dict['dep_name'] = department
                employee_dict['doj'] = doj
                employee_dict['dob'] = dob
                employee_dict['birthday'] = birthday
                employee_dict['company'] = company
                employees.append(employee_dict)
                
                
            
        #raise UserError(active_contract.ids)
                    
        return {
            'doc_ids': self.ids,
            'doc_model': 'employee.dob',
            'data': data,
            'active_contract': active_contract,
            'employees':employees
        }
