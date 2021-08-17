# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class HrUserAttendance(models.Model):
    _name = 'hr.user.attendance'
    _description = 'This is User Attendance'
    
    

    employee_id = fields.Many2one('hr.employee', string="Employee")
    is_mapped = fields.Boolean(string="Mapped Employee")
    company_id = fields.Many2one('res.company', string="Company")
    timestamp = fields.Datetime(string='Timestamp')
    device_id = fields.Char(string='Device ID')
    card_no = fields.Char(string="Card NO.")
    time = fields.Char(string="Stamp Time")
    attendance_date = fields.Date(string='Attendance Date')
    creation_date = fields.Char(string='Attendance Date')
    remarks = fields.Char(string='Remarks')
    updation_date = fields.Char(string='Updation Date')
    is_attedance_created = fields.Boolean(string="Attendance Posted")
    
      

   




    def action_attendace_validated(self):
        
        month_datetime = fields.date.today() - timedelta(2)
        for month_date in range(2):
            attendance_date1 =  month_datetime + timedelta(month_date)
            total_employee = self.env['hr.employee'].search([])
            for employee in total_employee:
                oracle_attendance = self.env['hr.user.attendance']
                count = oracle_attendance.search_count([('employee_id','=',employee.id)])
                attendance_list = oracle_attendance.search([('employee_id','=',employee.id),('attendance_date','=',attendance_date1),('is_attedance_created','=',False)], order="timestamp asc")
                if attendance_list: 
                    check_in = fields.date.today()
                    for attendace in attendance_list:
                        previous_attendance = attendace.attendance_date - timedelta(1)
                        pre_existing_attendance = self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=', previous_attendance),('check_out','=',False)] , order="check_in asc", limit=1)
                        if pre_existing_attendance.shift_id.shift_type == 'night':
                            pre_existing_attendance.update({
                                'check_out': attendace.timestamp,
                            }) 
                            attendace.update({
                                    'is_attedance_created' : True
                                    })         
                        else:
                            existing_attendance = self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=', attendace.attendance_date),('check_out','=',False)] , order="check_in asc", limit=1)
                            if existing_attendance:
                                delta_time = attendace.timestamp - existing_attendance.check_in  
                                delta = delta_time.total_seconds() 
                                if delta < 600 :
                                    existing_attendance.update({
                                    'check_in': attendace.timestamp,
                                    }) 
                                    attendace.update({
                                                    'is_attedance_created' : True
                                                    })
                                else:
                                    existing_attendance.update({
                                      'check_out': attendace.timestamp,
                                    }) 
                                    attendace.update({
                                                    'is_attedance_created' : True
                                                    })
                            else:    
                                vals = {
                                    'check_in': attendace.timestamp,
                                    'att_date': attendace.attendance_date,
                                    'employee_id': attendace.employee_id.id,
                                }   
                                attendance = self.env['hr.attendance'].create(vals)
                                attendace.update({
                                            'is_attedance_created' : True
                                            })
                                attendance.action_process_attendance(attendance.id)
                                