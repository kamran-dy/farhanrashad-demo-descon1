import xlwt
from odoo import models
from datetime import datetime, date
from odoo.exceptions import UserError


class ContractExpiryReport(models.AbstractModel):
    _name = 'report.de_hr_employee_report.cost_center_wise_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Cost Center Wise Report XLSX'
    
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
        costcenter = self.env['account.analytic.account'].search([('id', 'in', data['cost_center_ids'])])
        cost_centers = []
        for rec in costcenter:
            cost_centers.append(rec.name)
        #raise UserError(departments)
        cost_center = ','.join(cost_centers)
        
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
        
        format1 = workbook.add_format({'font_size': '14', 'align': 'vcenter', 'bold': True})
        sheet = workbook.add_worksheet('Cost Center Wise Report')
        
        sheet.write(3, 0, 'Cost Center', format1)
        sheet.write(3, 1, cost_center, format1)
        sheet.write(3, 4, 'Location', format1)
        sheet.write(3, 5, loc, format1)
        sheet.write(4, 0, 'Grade Type', format1)
        sheet.write(4, 1, gr_type, format1)
        sheet.write(4, 4, 'Employee Type', format1)
        sheet.write(4, 5, em_type, format1)
        
        
        sheet.write(6, 0, 'Cost Center', format1)
        sheet.write(6, 1, 'Grade Type', format1)
        sheet.write(6, 2, 'Employee Type', format1)
        sheet.write(6, 3, 'Emp Code', format1)
        sheet.write(6, 4, 'Name', format1)
        sheet.write(6, 5, 'Designation', format1)
        sheet.write(6, 6, 'Grade', format1)
        sheet.write(6, 7, 'DOJ', format1)
        
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
        
        
        for o in active_contract:
            if o.cost_center_information_line[0].cost_center:
                cost_center = o.cost_center_information_line[0].cost_center.name
            else:
                cost_center = None
            if o.employee_id.grade_type:
                grade_type = o.employee_id.grade_type.name
            else:
                grade_type = None
            if o.employee_id.emp_type:
                emp_type = o.employee_id.emp_type
            else:
                emp_type = None
            if o.employee_id.emp_number:
                emp_code = o.employee_id.emp_number
            else:
                emp_code = None
            if o.employee_id.name:
                name = o.employee_id.name
            else:
                name = None
            if o.job_id:
                designation = o.job_id.name
            else:
                designation = None
            if o.employee_id.grade_designation:
                grade = o.employee_id.grade_designation.name
            else:
                grade = None
            if o.employee_id.date:
                doj = o.employee_id.date.strftime("%Y/%m/%d")
            else:
                doj = None
            sheet.write(row, 0, cost_center, format2)
            sheet.write(row, 1, grade_type, format2)
            sheet.write(row, 2, emp_type, format2)
            sheet.write(row, 3, emp_code, format2)
            sheet.write(row, 4, name, format2)
            sheet.write(row, 5, designation, format2)
            sheet.write(row, 6, grade, format2)
            sheet.write(row, 7, doj, format2)
            
            row = row + 1
            