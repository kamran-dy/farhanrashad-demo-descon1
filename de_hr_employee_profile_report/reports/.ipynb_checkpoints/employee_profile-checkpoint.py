from odoo import api, models, _
from odoo.exceptions import UserError


class EmployeeProfilePDF(models.AbstractModel):
    _name = 'report.de_hr_employee_profile_report.employee_profile_report'
    _description = 'Employee Profile PDF Report'

    @api.model
    def _get_report_values(self, docids, data):
        employee = self.env['hr.employee'].search([('id', '=', docids)])
        employee_contract = self.env['hr.contract'].search([('employee_id', '=', employee.name)])
        employee_leaves = self.env['hr.leave.report'].search([('employee_id', '=', employee.name)])
        employee_appraisal = self.env['hr.appraisal'].search([('employee_id', '=', employee.name)])
        employee_training = self.env['employee.training'].search([('employee_id', '=', employee.name)])
        
        
        annual_leave_count = 0
        sick_leave_count = 0
        casual_leave_count = 0
        for leave in employee_leaves:
            if leave.holiday_status_id.name == 'Annual Leave':
                annual_leave_count = annual_leave_count + 1
            elif leave.holiday_status_id.name == 'Sick Leave':
                sick_leave_count = sick_leave_count + 1
            elif leave.holiday_status_id.name == 'Casual Leave':
                casual_leave_count = casual_leave_count + 1
#         raise UserError(employee.resume_line_ids[1].name)
#         names = ''
#         for resume in employee.resume_line_ids:
#             if resume.line_type_id.name == 'Education':
#                 names = names + resume.name + ' '
# #             raise UserError(resume.name)
#         raise UserError(names)
       
        #family = list(zip(employee.employee_family_ids,employee.resume_line_ids))
#         print(family[0])
        cost_center = employee_contract.cost_center_information_line[0].cost_center
        cost_center_percentage = employee_contract.cost_center_information_line[0].percentage_charged
        cost_center_start_date = employee_contract.date_start
    
        #raise UserError(family[0])
        
        return {
            'doc_ids': self.ids,
            'doc_model': 'hr.employee',
            'employee':employee,
            'employee_contract':employee_contract,
            'cost_center':cost_center,
            'cost_center_percentage':cost_center_percentage,
            'cost_center_start_date':cost_center_start_date,
            'annual_leave_count':annual_leave_count,
            'sick_leave_count':sick_leave_count,
            'casual_leave_count':casual_leave_count,
            'employee_appraisal':employee_appraisal,
            'employee_training':employee_training,
        }