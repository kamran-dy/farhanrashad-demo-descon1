from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class EmployeeDobWizard(models.TransientModel):
    _name = 'employee.dob'
    _description = 'Employee DOB Wizard'

    company_ids = fields.Many2many('res.company', string='Companies')
    
            
    def action_generate_pdf(self):
        data = {
            'company_ids': self.company_ids.ids,
            }
        return self.env.ref('de_hr_employee_report.employee_dob').report_action(self, data=data)