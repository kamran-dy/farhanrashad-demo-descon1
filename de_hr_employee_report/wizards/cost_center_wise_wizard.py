from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CostCenterWise(models.TransientModel):
    _name = 'cost.center.wise'
    _description = 'Cost Center Wise'

    employee_type_ids = fields.Many2many('employee.type', string='Employee`s Type')
    grade_type_ids = fields.Many2many('grade.type', string='Grade Type')
    #location_ids = fields.Many2one('hr.location', string='Location')
    location_ids = fields.Many2many('hr.work.location', string='Location')
    cost_center_ids = fields.Many2many('account.analytic.account', string='Cost Center')

    def action_generate_pdf(self):
#         employee_type_names = []
#         for ids in self.employee_type_ids:
#             employee_type_names.append(ids.name)
        data = {
            'employee_type_ids': self.employee_type_ids.ids,
            'grade_type_ids': self.grade_type_ids.ids,
            'location_ids': self.location_ids.ids,
            'cost_center_ids': self.cost_center_ids.ids, }
        return self.env.ref('de_hr_employee_report.action_report_cost_center_wise').report_action(self, data=data)

    def action_gnerate_excel(self):
        employee_type_names = []
        for ids in self.employee_type_ids:
            employee_type_names.append(ids.name)
        data = {
            'employee_type_ids': self.employee_type_ids.ids,
            'grade_type_ids': self.grade_type_ids.ids,
            'location_ids': self.location_ids.ids,
            'cost_center_ids': self.cost_center_ids.ids, }
        return self.env.ref('de_hr_employee_report.view_cost_center_wise_report_xlsx').report_action(self, data=data)
