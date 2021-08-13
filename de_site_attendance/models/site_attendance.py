from odoo import api, fields, models, _
from calendar import monthrange

from odoo.exceptions import UserError


class SiteAttendnace(models.Model):
    _name = 'hr.attendance.site'
    _description = 'Site Attendance'
    _inherit = ['mail.thread']
    _rec_name = 'incharge_id'

   
    incharge_id = fields.Many2one('hr.employee', string='Site Incharge')
    
    category_id = fields.Many2one(related='incharge_id.category_id', string='Approval Category')
    approval_request_id = fields.Many2one('approval.request', string="Approval")
    location_id = fields.Many2one(related='incharge_id.work_location_id', string='Site Location')
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'),('refused', 'Refused')], string='Status',
                             default='draft')    
    attendance_line_ids = fields.One2many('hr.attendance.site.line', 'site_id', string="Site Lines")
    
    
    @api.constrains('employee_id')
    def _check_incharge(self):
        for line in self:
            if line.employee_id:
                if line.employee_id.site_incharge_id.user_id.id != self.env.uid:                   
                    raise UserError('Only Employee Site Incharge can Mark Attendace!')
                    
                    
    @api.model
    def create(self, vals):
        sheet = super(SiteAttendnace, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)).create(vals)
        sheet.action_submit()
        sheet.action_create_approval_request_site_attendance()
        
        return sheet
    
    
    def action_create_approval_request_site_attendance(self):
        approver_ids  = []
        
        
        request_list = []
        for line in self:
            if line.category_id:
                request_list.append({
                        'name': line.incharge_id.name + ' Has Site Attendance Request Location ' + str(line.location_id.name)+ ' Date From ' + str(line.date_from)+' '+' Date To '+str(line.date_to),
                        'request_owner_id': line.incharge_id.user_id.id,
                        'category_id': line.category_id.id,
                        'site_id': line.id,
                        'reason': line.incharge_id.name + ' Has Site Attendance Request Location ' + str(line.location_id.name)+ ' Date From ' + str(line.date_from)+' '+' Date To '+str(line.date_to) ,
                        'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].create(request_list)
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                line.approval_request_id = approval_request_id.id
                
            
        

    def unlink(self):
        for line in self:
            if line.state != 'draft':
                raise UserError('A record in Submitted or Approved state can`t be deleted!')
        return super(SiteAttendnace, self).unlink()

    def action_submit(self):
        self.state = 'submitted'
        for line in self.attendance_line_ids:
            line.update({
                'state': 'submitted'
            })
            
            
    def action_refuse(self):
        self.state = 'refused'
        for line in self.attendance_line_ids:
            line.update({
                'state': 'refused'
            })         
            

    def action_approved(self):
        self.state = 'approved'
        for line in self.attendance_line_ids:
            if line.normal_overtime > 0:
                employee_company = line.employee_id.company_id.id
                work_location = line.employee_id.work_location_id.id
                overtime_type = self.env['hr.overtime.type'].search([('type','=','normal'),('company_id','=',employee_company)], limit=1)
                if not overtime_type:
                    overtime_type = self.env['hr.overtime.type'].search([('type','=','normal')], limit=1)
                if work_location:
                    overtime_type = self.env['hr.overtime.type'].search([('type','=','normal'),('company_id','=',employee_company),('work_location_id','=',work_location)], limit=1)
                    if not overtime_type:
                        if employee_company:
                            overtime_type = self.env['hr.overtime.type'].search([('type','=','normal'),('company_id','=',employee_company)], limit=1)
                            if not overtime_type:
                                overtime_type = self.env['hr.overtime.type'].search([('type','=','normal')], limit=1)

                vals = {
                    'employee_id': line.employee_id.id,
                    'company_id': line.employee_id.company_id.id,
                    'date':  self.date_from,
                    'date_from': self.date_from,
                    'date_to': self.date_from,
                    'hours': line.days,
                    'overtime_hours': line.normal_overtime,
                    'overtime_type_id': overtime_type.id,     
                        }
                overtime_lines = self.env['hr.overtime.request'].create(vals)  
                
            if line.gazetted_overtime > 0:
                employee_company = line.employee_id.company_id.id
                work_location = line.employee_id.work_location_id.id
                overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted')], limit=1) 
                if employee_company:
                    overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted'),('company_id','=',employee_company)], limit=1)
                    if not overtime_type:
                        overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted')], limit=1) 

                        if work_location: 
                            overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted'),('company_id','=',employee_company),('work_location_id','=',work_location)], limit=1)
                            if not overtime_type:
                                if employee_company:
                                    overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted'),('company_id','=',employee_company)], limit=1)
                                    if not overtime_type:
                                        overtime_type = self.env['hr.overtime.type'].search([('type','=','gazetted')], limit=1) 
                                        

                vals = {
                    'employee_id': line.employee_id.id,
                    'company_id': line.employee_id.company_id.id,
                    'date':  self.date_from,
                    'date_from': self.date_from,
                    'date_to': self.date_from,
                    'hours': line.days,
                    'overtime_hours': line.gazetted_overtime,
                    'overtime_type_id': overtime_type.id,     
                        }
                overtime_lines = self.env['hr.overtime.request'].create(vals)       
                
            line.update({
                'state': 'approved'
            })

    def action_reset(self):
        self.state = 'draft'
        for line in self.attendance_line_ids:
            line.update({
                'state': 'draft'
            })

   
class SiteAttendnaceline(models.Model):
    _name = 'hr.attendance.site.line'
    _description = 'Site Attendance'
    _rec_name = 'employee_id'

    site_id = fields.Many2one('hr.attendance.site', string='Site Attendance')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=False)
    char = fields.Char(string='Test')
    incharge_id = fields.Many2one(related='employee_id.site_incharge_id', string='Site Incharge')
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'),('refused', 'Refused')], string='Status',
                             default='draft')    
    days = fields.Float(string='Total Days')
    normal_overtime = fields.Float(string="Normal Overtime")
    gazetted_overtime = fields.Float(string="Gazetted Overtime")
    
    
    def unlink(self):
        for line in self:
            if line.state != 'draft':
                raise UserError('A record in Submitted or Approved state can`t be deleted!')
        return super(SiteAttendnaceline, self).unlink()


    
    
    @api.constrains('employee_id')
    def _check_incharge(self):
        for line in self:
            if line.employee_id:
                if line.employee_id.site_incharge_id.user_id.id != self.env.uid:                   
                    raise UserError('Only Employee Site Incharge can Mark Attendace!')
   
