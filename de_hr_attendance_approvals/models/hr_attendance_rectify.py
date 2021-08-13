# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError



class HrAttendanceRectification(models.Model):
    _name = 'hr.attendance.rectification'
    _description = 'Attendance Rectification'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    user_id = fields.Many2one('res.users', string="User")
    category_id = fields.Many2one(related='employee_id.category_id')
    check_in = fields.Datetime(string="Check In", required=False)
    check_out = fields.Datetime(string="Check Out", required=False)
    approval_request_id = fields.Many2one('approval.request', string="Approval")
    date = fields.Date(string="Date")
    reason =  fields.Text(string="Reason")
    partial = fields.Char(string='Type')
    attendance_id = fields.Many2one('hr.attendance', string="Attendance")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
         ],
        readonly=True, string='State', default='draft')
    
    @api.constrains('check_in', 'check_out')
    def _check_attendance_date(self):
        for line in self:
            if line.check_in:
                line.update({
                    'date': line.check_in
                })
            elif line.check_out:
                line.update({
                    'date': line.check_out
                })    
    
    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                hr_attendance = self.env['hr.attendance'].search([('employee_id','=',attendance.employee_id.id),('att_date','=',attendance.date)])
                for line in hr_attendance:
                    if line.check_in and line.check_out:
                        if str(attendance.check_in) >= str(line.check_in) and str(attendance.check_in) <= str(line.check_out):
                            raise exceptions.UserError(_('Attendance Already Exist between selected range!'))
                                    
                if attendance.check_out < attendance.check_in:
                    raise exceptions.UserError(_('"Check Out" time cannot be earlier than "Check In" time.'+ str(attendance.check_out) ))
                     
               
    
    def action_submit(self):
        for line in self:
            line.update({
                'state': 'submitted'
            })
            
    def action_approve(self):
        for line in self:
            if line.state == 'submitted':
                
                if line.attendance_id:
                    attendance_rectify = self.env['hr.attendance'].search([('id','=',line.attendance_id.id)])

                    attendance_rectify.update({
                        'check_in': line.check_in,
                        'check_out': line.check_out,
                    })
                    line.update({
                        'state': 'approved'
                    })
                elif line.date:
                    attendance_rectify = self.env['hr.attendance'].search([('employee_id','=',line.employee_id.id),('att_date','=', line.date)])
                    if attendance_rectify:
                        for rectify_attendance in attendance_rectify:
                            if rectify_attendance.check_in and rectify_attendance.check_out:
                                if line.check_out and line.check_in:
                                    if rectify_attendance.check_in >= line.check_in and  rectify_attendance.check_in >= line.check_out:
                                        pass
                                    else:
                                        vals = {
                                            'employee_id': line.employee_id.id,
                                            'check_in': line.check_in,
                                            'check_out': line.check_out,
                                            'remarks': 'Comitment Slip',
                                        }
                                        attendance = self.env['hr.attendance'].create(vals)
                                        line.update({
                                            'state': 'approved'
                                        }) 
                                    
                            elif rectify_attendance.check_in:
                                if line.check_out:
                                    if rectify_attendance.check_in > line.check_out:                           
                                        rectify_attendance.update({
                                            'check_in': line.check_out,
                                            'check_out': rectify_attendance.check_in,
                                            'remarks': 'In Time Is Missing',
                                        })
                                    elif rectify_attendance.check_in < line.check_out: 
                                        rectify_attendance.update({
                                            'check_in': rectify_attendance.check_in,
                                            'check_out': line.check_out,
                                            'remarks': 'Out Time Is Missing',
                                        })
                                elif  line.check_in:
                                    if rectify_attendance.check_in > line.check_in:                           
                                        rectify_attendance.update({
                                            'check_in': line.check_in,
                                            'check_out': rectify_attendance.check_in,
                                            'remarks': 'In Time Is Missing',
                                        })
                                    elif rectify_attendance.check_in < line.check_in: 
                                        rectify_attendance.update({
                                            'check_in': rectify_attendance.check_in,
                                            'check_out': line.check_in,   
                                            'remarks': 'Out Time Is Missing',
                                        }) 
                                        
                    else:
                        vals = {
                            'employee_id': line.employee_id.id,
                            'check_in': line.check_in,
                            'check_out': line.check_out,
                            'remarks': 'Comitment Slip',
                        }
                        attendance = self.env['hr.attendance'].create(vals)
                        line.update({
                            'state': 'approved'
                        })                     
                    line.update({
                        'state': 'approved'
                    })
                else:
                    vals = {
                        'employee_id': line.employee_id.id,
                        'check_in': line.check_in,
                        'check_out': line.check_out,
                        'remarks': 'Comitment Slip',
                        
                    }
                    attendance = self.env['hr.attendance'].create(vals)
                    line.update({
                        'state': 'approved'
                    }) 
                
            
    def action_refuse(self):
        for line in self:
            line.update({
                'state': 'refused'
            })
            rectification_approval = self.env['approval.request'].search([('rectification_id','=', line.id)], limit=1)
            rectification_approval.action_cancel()
            
            
            
            
            
    @api.model
    def create(self, vals):
        sheet = super(HrAttendanceRectification, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)).create(vals)
        if sheet.category_id:
            sheet.action_create_approval_request_attendance()
        sheet.action_validate_comitment_period()
        return sheet
    
    def action_validate_comitment_period(self):
        restrict_date = '2021-07-16'
        for line in self:
            if str(line.date)  <= restrict_date:
                raise UserError('Not Allow to Enter Rectification Request before 16 JULY 2021!') 
    
    def action_create_approval_request_attendance(self):
        approver_ids  = []
        
        
        request_list = []
        for line in self:
            if line.category_id:
                request_list.append({
                        'name':  str(line.employee_id.name ),
                        'request_owner_id': line.employee_id.user_id.id,
                        'category_id': line.category_id.id,
                        'rectification_id': line.id,
                        'reason': ' Check In: ' + str(line.check_in + relativedelta(hours =+ 5))+"\n"+' Check Out: '+str(line.check_out+ relativedelta(hours =+ 5))+"\n" +"\n" +"\n" + ' Remarks:   ' +str(line.reason)+"\n",
                        'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].create(request_list)
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                line.approval_request_id = approval_request_id.id


    
    

    