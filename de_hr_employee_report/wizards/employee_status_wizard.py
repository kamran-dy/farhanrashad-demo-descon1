from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EmployeeStatus(models.TransientModel):
    _name = 'employee.status'
    _description = 'Employee Status'

    employee_type_ids = fields.Many2many('employee.type', string='Employee`s Type')
    location_ids = fields.Many2many('hr.work.location', string='Location')
    cost_center_ids = fields.Many2many('account.analytic.account', string='Cost Center')
    department_ids = fields.Many2many('hr.department', string='Department')
    company_ids = fields.Many2many('res.company', string='Companies')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    

    def action_generate_pdf(self):
        data = {
            'employee_type_ids': self.employee_type_ids.ids,
            'department_ids': self.department_ids.ids,
            'location_ids': self.location_ids.ids,
            'cost_center_ids': self.cost_center_ids.ids,
            'start_date':self.start_date,
            'end_date':self.end_date,
            'company_ids': self.company_ids.ids}
        return self.env.ref('de_hr_employee_report.action_report_employee_status').report_action(self, data=data)

