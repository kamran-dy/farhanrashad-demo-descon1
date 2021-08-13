import json
from odoo import models
from odoo.exceptions import UserError


class GenerateXLSXReport(models.Model):
    _name = 'report.de_payslip_salary_report.payslip_salary_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format({'font_size': '12', 'align': 'vcenter', 'bold': True})
        sheet = workbook.add_worksheet('Salary Details Report')
        sheet.write(3, 0, 'Company Name', format1)
        sheet.write(3, 1, 'Location', format1)
        sheet.write(3, 2, 'Dept Name', format1)
        sheet.write(3, 3, 'Period', format1)
        sheet.write(3, 4, 'Name', format1)
        sheet.write(3, 5, 'Doj', format1)
        sheet.write(3, 6, 'Dob', format1)
        sheet.write(3, 7, 'Position', format1)
        sheet.write(3, 8, 'Grade', format1)
        sheet.write(3, 9, 'Grade Type', format1)
        sheet.write(3, 10, 'Nic No.', format1)
        sheet.write(3, 11, 'Bank Name', format1)
        sheet.write(3, 12, 'Bank Account', format1)
    
        format2 = workbook.add_format({'font_size': '12', 'align': 'vcenter'})
        row = 4
        sheet.set_column(row, 0, 50)
        sheet.set_column(row, 1, 25)
        sheet.set_column(row, 2, 25)
        sheet.set_column(row, 3, 25)
        sheet.set_column(row, 4, 25)
        sheet.set_column(row, 5, 25)
        sheet.set_column(row, 6, 25)
        sheet.set_column(row, 7, 25)
        sheet.set_column(row, 8, 25)
        sheet.set_column(row, 9, 25)
        sheet.set_column(row, 10, 25)
        sheet.set_column(row, 11, 25)
        sheet.set_column(row, 12, 25)
        
        
        for id in lines:
            if id.date_end:
                date_end = id.date_end
                date_end = date_end.strftime("%d/%m/%Y")
            else:
                date_end = None
            payslips = self.env['hr.payslip'].search([('payslip_run_id','=',id.name)])
            for payslip in payslips:
                if payslip.company_id:
                    company = payslip.company_id.name
                else:
                    company = None
                    
                employee = self.env['hr.employee'].search([('name','=',payslip.employee_id.name)])[0]
                
                if employee.department_id:
                    department = employee.department_id.name
                else:
                    department = None
                
                if employee.work_location:
                    location = employee.work_location
                else:
                    location = None
                    
                if employee.name:
                    name = employee.name
                else:
                    name = None
                
                if employee.date:
                    doj = employee.date
                    doj = doj.strftime("%d/%m/%Y")
                else:
                    doj = None
                 
                if employee.birthday:
                    dob = employee.birthday
                    dob = dob.strftime("%d/%m/%Y")
                else:
                    dob = None
                
                if employee.job_id:
                    job_position = employee.job_id.name
                else:
                    job_position = None
                
                if employee.cnic:
                    cnic = employee.cnic
                else:
                    cnic = None
                
                if employee.bank_account_id.bank_id:
                    bank_name = employee.bank_account_id.bank_id.name
                else:
                    bank_name = None
                
                if employee.bank_account_id:
                    bank_account = employee.bank_account_id.acc_number
                else:
                    bank_account = None
                
                if employee.grade_designation:
                    grade_designation = employee.grade_designation.name
                else:
                    grade_designation = None
                
                if employee.grade_type:
                    grade_type = employee.grade_type.name
                else:
                    grade_type = None
                
                sheet.write(row, 0, company, format2)
                sheet.write(row, 1, location, format2)
                sheet.write(row, 2, department, format2)
                sheet.write(row, 3, date_end, format2)
                sheet.write(row, 4, name, format2)
                sheet.write(row, 5, doj, format2)
                sheet.write(row, 6, dob, format2)
                sheet.write(row, 7, job_position, format2)
                sheet.write(row, 8, grade_designation, format2)
                sheet.write(row, 9, grade_type, format2)
                sheet.write(row, 10, cnic, format2)
                sheet.write(row, 11, bank_name, format2)
                sheet.write(row, 12, bank_account, format2)
                
                row = row + 1
                
                
                    