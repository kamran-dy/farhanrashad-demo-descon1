# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class CostCenterDistributionPDF(models.AbstractModel):
    _name = 'report.de_hr_employee_report.cost_center_distribution_pdf'
    _description = 'Cost Center Distribution PDF Report'

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
        location = self.env['hr.work.location'].search([('id', 'in', data['location_ids'])])
        locations = []
        for rec in location:
            locations.append(rec.name)
        
        loc = ','.join(locations)
        costcenter = self.env['account.analytic.account'].search([('id', 'in', data['cost_center_ids'])])
        cost_centers = []
        for rec in costcenter:
            cost_centers.append(rec.name)
        #raise UserError(departments)
        cost_center = ','.join(cost_centers)
#         em_type = ''
#         em_type = ','.join(data['employee_type_ids'])
        
#         employee_type = data['employee_type_ids']
#         grade_type = data['grade_type_ids']
#         location = data['location_ids']
#         cost_center = data['cost_center_ids']
        
        if employee_type and grade_type and location and cost_center:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.grade_type', 'in', g_type),
                                                              ('employee_id.work_location_id', 'in',locations),
                                                              ('cost_center_information_line.cost_center', 'in',
                                                               cost_centers)])
        elif employee_type and grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.grade_type', '=', g_type)])
        elif employee_type and location:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.work_location_id', '=',locations)])
        elif employee_type and cost_center:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('cost_center_information_line.cost_center', '=',
                                                               cost_centers)])
        elif employee_type and grade_type and location:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.grade_type', '=', g_type),
                                                              ('employee_id.work_location_id', '=',locations)
                                                              ])
        elif employee_type and grade_type and cost_center:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.grade_type', '=', g_type),
                                                              ('cost_center_information_line.cost_center', '=',
                                                               cost_centers)
                                                              ])
        elif employee_type and location and cost_center:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.work_location_id', '=',location),
                                                              ('cost_center_information_line.cost_center', '=',
                                                               cost_centers)
                                                              ])
        return {
            'doc_ids': self.ids,
            'doc_model': 'cost.center.distribution',
            'data': data,
            'location': loc,
            'employee_type': em_type,
            'grade_type': gr_type,
            'cost_center': cost_center,
            'active_contract': active_contract,
        }
