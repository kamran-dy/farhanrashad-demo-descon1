from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class EmployeeExperienceWizard(models.TransientModel):
    _name = 'employee.experience'
    _description = 'Employee Experience Wizard'

    employee_type_ids = fields.Many2many('employee.type', string='Employee`s Type')
    grade_type_ids = fields.Many2many('grade.type', string='Grade Type')
    company_ids = fields.Many2many('res.company', string='Companies')
    
    
    def action_generate_pdf(self):
        data = {
            'employee_type_ids': self.employee_type_ids.ids,
            'grade_type_ids': self.grade_type_ids.ids,
            'company_ids': self.company_ids.ids,
            }
        return self.env.ref('de_hr_employee_report.employee_experience').report_action(self, data=data)