from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class EmployeeAge(models.TransientModel):
    _name = 'employee.age'
    _description = 'Employee Age'

    department_ids = fields.Many2many('hr.department', string='Department')
    employee_type_ids = fields.Many2many('employee.type', string='Employee`s Type')
    grade_type_ids = fields.Many2many('grade.type', string='Grade Type')
    location_ids = fields.Many2many('hr.work.location', string='Location')
    age_from = fields.Integer('Age From')
    age_to = fields.Integer('Age To')
    
    @api.constrains('age_to')
    def check_age(self):
        for rec in self:
            if (rec.age_to < 18) and (rec.age_to > 100):
                #raise UserError('Age must be between 18 and 100')
                raise ValidationError(_('Age must be between 18 and 100'))
    
    @api.constrains('age_from')
    def check_age(self):
        for rec in self:
            if (rec.age_from < 18) and (rec.age_from > 100):
                #raise UserError('Age must be between 18 and 100')
                raise ValidationError(_('Age must be between 18 and 100'))
            

    def action_generate_pdf(self):
        data = {
            'employee_type_ids': self.employee_type_ids.ids,
            'grade_type_ids': self.grade_type_ids.ids,
            'location_ids': self.location_ids.ids,
            'department_ids': self.department_ids.ids,
            'age_from': self.age_from,
            'age_to':self.age_to
            }
        return self.env.ref('de_hr_employee_report.action_report_employee_age').report_action(self, data=data)

    def action_gnerate_excel(self):
        data = {
            'employee_type_ids': self.employee_type_ids.ids,
            'grade_type_ids': self.grade_type_ids.ids,
            'location_ids': self.location_ids.ids,
            'department_ids': self.department_ids.ids,
            'age_from': self.age_from,
            'age_to':self.age_to
            }
        return self.env.ref('de_hr_employee_report.view_employee_age_report_xlsx').report_action(self, data=data)
