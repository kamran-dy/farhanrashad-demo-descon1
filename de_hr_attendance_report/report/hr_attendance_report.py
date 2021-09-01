# -*- coding: utf-8 -*-

import time
from odoo import api, models, _ , fields 
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class PurchaseAttendanceReport(models.AbstractModel):
    _name = 'report.de_hr_attendance_report.attendance_report'
    _description = 'Hr Attendance Report'

    
    
    
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        employees_attendance = []
        portal_employee = []
        
        for employee11 in docs.employee_ids:
            work_day_line = [] 
            
            employee = self.env['hr.employee'].sudo().search([('id',
                                                       '=', employee11.id)], limit=1)
            date_from = datetime.strptime(str(docs.start_date), "%Y-%m-%d")
            date_to = datetime.strptime(str(docs.end_date), "%Y-%m-%d")

            work_days = 0
            work_hours = 0 
            
            """
              Employee Attendance Days
            """ 
            emp_attendance = self.env['hr.attendance'].sudo().search([('employee_id','=', employee.id),('att_date','>=', date_from),('att_date','<=', date_to)])
            previous_date = fields.date.today()
            work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','WORK100')], limit=1)
            for attendance in emp_attendance:
                if attendance.check_out:
                    new_date = attendance.check_out.strftime('%y-%m-%d')
                    if new_date != previous_date:
                        daily_leave = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('request_date_from','<=', attendance.att_date),('request_date_to','>=',  attendance.att_date),('state','in',('validate','confirm'))])
                        if daily_leave.number_of_days == 0.5:
                            work_days += 0.5
                            work_hours += attendance.worked_hours / 2
                            
                        elif  daily_leave.number_of_days == 0.25:
                            work_days += 0.75
                            att_hours = attendance.worked_hours / 4 
                            work_hours += attendance.worked_hours - att_hours
                        else:     
                            work_days += 1
                            work_hours += attendance.worked_hours 
                    previous_date = attendance.check_out.strftime('%y-%m-%d')
            work_day_line.append({
               'work_entry_type_id' : work_entry_type.id ,
               'name': work_entry_type.name ,
               'sequence': work_entry_type.sequence ,
               'number_of_days' : work_days ,
               'number_of_hours' : work_hours ,
            })
                      
            """
              Employee Timoff by Timeoff type wise
            """ 
            
            leave_type = []
            
            total_leave_days = 0
            emp_leaves = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('date_from','>=', date_from),('date_to','<=', date_to),('state','in',('validate','confirm')),('holiday_status_id.is_rest_day','=',False)])
            previous_date = fields.date.today()
            leave_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','LEAVE100')], limit=1)
            for leave in emp_leaves: 
                leave_type.append(leave.holiday_status_id.id)
            uniq_leave_type = set(leave_type)
            for timeoff_type in uniq_leave_type:
                leave_work_days = 0
                leaves_work_hours = 0 
                emp_leaves_type = self.env['hr.leave'].sudo().search([('holiday_status_id','=', timeoff_type),('employee_id','=', employee.id),('date_from','>=', date_from),('date_to','<=', date_to),('state','in',('validate','confirm'))])
                for timeoff in emp_leaves_type:
                    leave_work_days += timeoff.number_of_days
                    total_leave_days += timeoff.number_of_days 
                timeoff_vals = self.env['hr.leave.type'].sudo().search([('id','=',timeoff_type)], limit=1) 
                
                timeoff_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=',timeoff_vals.name)], limit=1)
                if not timeoff_work_entry_type:
                    vals = {
                        'name': timeoff_vals.name,
                        'code': timeoff_vals.name,
                        'round_days': 'NO',
                    }
                    work_entry = self.env['hr.work.entry.type'].sudo().create(vals)
                timeoff_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=',timeoff_vals.name)], limit=1)

                work_day_line.append({
                   'work_entry_type_id' : timeoff_work_entry_type.id,
                   'name': timeoff_work_entry_type.name,
                   'sequence': timeoff_work_entry_type.sequence,
                   'number_of_days' : leave_work_days,
                   'number_of_hours' : leave_work_days * employee.shift_id.hours_per_day ,
                })               
                
            """
              Employee Absent Days
            """ 
            absent_work_days_initial = 0
            delta = date_from - date_to
            total_days = abs(delta.days)
            for i in range(0, total_days + 1):
                absent_work_days_initial = absent_work_days_initial + 1
            rest_days_initial = 0
            gazetted_days_count = 0
            absent_work_days = 0
            shift_contract_lines = self.env['hr.shift.schedule.line'].sudo().search([('employee_id','=', employee.id),('date','>=',date_from),('date','<=',date_to),('state','=','posted')])
            for shift_line in shift_contract_lines:
                if shift_line.first_shift_id:
                    for gazetted_day in shift_line.first_shift_id.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                        gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                        if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            gattendance = self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=',shift_line.date)])
                            gdaily_leave = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('request_date_from','<=', shift_line.date),('request_date_to','>=', shift_line.date),('state','in',('validate','confirm'))]) 
                            if gattendance:
                                pass
                            elif gdaily_leave:
                                pass
                            else:
                                gazetted_days_count += 1 
                else:
                    current_shift = employee.shift_id
                    if not current_shift:
                        current_shift = self.env['resource.calendar'].sudo().search([('company_id','=', employee.company_id.id)], limit=1)
                    if not current_shift:
                        current_shift = self.env['resource.calendar'].sudo().search([], limit=1)

                    for gazetted_day in current_shift.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                        gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                        if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            gattendance = self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=',shift_line.date)])
                            gdaily_leave = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('request_date_from','<=', shift_line.date),('request_date_to','>=', shift_line.date),('state','in',('validate','confirm'))]) 
                            if gattendance:
                                pass
                            elif gdaily_leave:
                                pass
                            else:
                                gazetted_days_count += 1
                if shift_line.rest_day == True:
                    exist_attendance = self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=',shift_line.date)])
                    if  exist_attendance.check_in and exist_attendance.check_out:
                        pass
                    else:
                        rest_days_initial += 1  
                    if shift_line.first_shift_id:
                        for gazetted_day in shift_line.first_shift_id.global_leave_ids:
                            gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                            gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                            if str(shift_line.date) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                                rest_days_initial -= 1     
                    else:
                        
                        current_shift = self.env['resource.calendar'].sudo().search([], limit=1)
                        current_shift = self.env['resource.calendar'].sudo().search([('company_id','=', employee.company_id.id)], limit=1)
                        for gazetted_day in current_shift.global_leave_ids:
                            gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                            gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                            if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                                rest_days_initial -= 1 
                        
                                   
            work_day_line.append({
                   'work_entry_type_id' : 1,
                   'name': 'Gazetted Holidays',
                   'sequence': 2,
                   'number_of_days' : gazetted_days_count,
                   'number_of_hours' : gazetted_days_count * employee.shift_id.hours_per_day ,
            })   
            
            """
              Rest Day 
            """
            rest_day_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','Rest Day')], limit=1)
            
            if not rest_day_work_entry_type:
                vals = {
                    'name': 'Rest Day',
                    'code': 'Rest Day',
                    'round_days': 'NO',
                }
                work_entry = self.env['hr.work.entry.type'].sudo().create(vals)  
            rest_day_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','Rest Day')], limit=1)    
            work_day_line.append({
               'work_entry_type_id' : rest_day_work_entry_type.id,
               'name': rest_day_work_entry_type.name,
               'sequence': rest_day_work_entry_type.sequence,
               'number_of_days' : rest_days_initial ,
               'number_of_hours' : rest_days_initial * employee.shift_id.hours_per_day ,
            })
            absent_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','ABSENT100')], limit=1)
            if not absent_work_entry_type:
                vals = {
                    'name': 'Absent Days',
                    'code': 'ABSENT100',
                    'round_days': 'NO',
                }
                work_entry = self.env['hr.work.entry.type'].sudo().create(vals)
            apply_leave_days = 0    
            emp_leaves_apply = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('date_from','>=', date_from),('date_to','<=', date_to),('state','=','validate')]) 
            for leave_apply in emp_leaves_apply:
                apply_leave_days += leave_apply.number_of_days
            
            absent_work_days = absent_work_days_initial - (gazetted_days_count + rest_days_initial + total_leave_days + work_days)
            absent_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','ABSENT100')], limit=1)
            
            work_day_line.append({
               'work_entry_type_id' : absent_work_entry_type.id,
               'name': absent_work_entry_type.name,
               'sequence': absent_work_entry_type.sequence,
               'number_of_days' : absent_work_days if absent_work_days > 0.0 else 0,
               'number_of_hours' : (absent_work_days if absent_work_days > 0.0 else 0) * employee.shift_id.hours_per_day ,
            })
            


    
            attendances = []
            delta = date_from - date_to
            total_days = abs(delta.days)
            rest_day_count = 0
            for i in range(0, total_days + 1):            
                day = ' '
                remarks = ' '
                rest_day = 'N'                    

                date_after_month = date_from + relativedelta(days=i)

                hr_attendance = self.env['hr.attendance'].search([('employee_id','=', employee.id),('att_date','=', date_after_month)]) 
                if hr_attendance:
                    datecheck_in_time  = ' '
                    datecheck_out_time = ' '
                    day1 = date_after_month.strftime('%A')
                    shift = employee.shift_id.name
                    tot_hours = 0
                    rest_day = 'N'
                    remarks = ' '
                    current_shift = employee.shift_id
                    for attendance in hr_attendance:
                        tot_hours +=  attendance.worked_hours
                        emp_leaves = self.env['hr.leave'].search([('employee_id','=', employee.id),('request_date_from','=', date_after_month)], limit=1)
                        shift = attendance.shift_id.name
                        if not shift:
                            shift = attendance.employee_id.shift_id.name
                        current_shift = attendance.shift_id
                        if  attendance.check_out and attendance.check_in:
                            remarks = 'Attendance Present.'
                        elif not attendance.check_out and attendance.check_in:
                            remarks = 'Check Out is Missing' 
                        elif not attendance.check_in and attendance.check_out: 
                            remarks = 'Check In is Missing'
                        elif emp_leaves:
                            remarks = str(emp_leaves.holiday_status_id.name)
                        else:
                            remarks = 'Absent.'
                        if not  shift:   
                            shift = self.env['resource.calendar'].search([], limit=1).name
                            shift = self.env['resource.calendar'].search([('company_id','=', employee.company_id.id)], limit=1).name
                            current_shift = self.env['resource.calendar'].search([], limit=1)
                            current_shift = self.env['resource.calendar'].search([('company_id','=', employee.company_id.id)], limit=1)
                            shift_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month)], limit=1)
                            if shift_line.first_shift_id:
                                shift = shift_line.first_shift_id.name
                                current_shift = attendance.shift_id
                            elif shift_line.second_shift_id:
                                shift = shift_line.second_shift_id.name
                                current_shift = attendance.shift_id

                        rest_schedule_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month),('rest_day','=', True)], limit=1)

                        if rest_schedule_line:
                            rest_day = 'Y'    
                            remarks = 'Restday.'
                            rest_day_count += 1 


                        day1 = date_after_month.strftime('%A')    

                        check_in_time =  attendance.check_in
                        check_out_time = attendance.check_out
                        if  attendance.check_in:
                            check_in_time = attendance.check_in + relativedelta(hours =+ 5)

                        if  attendance.check_out:
                            check_out_time = attendance.check_out + relativedelta(hours =+ 5)
                        datecheck_in_time = check_in_time
                        datecheck_out_time = check_out_time
                        if check_in_time :
                            datecheck_in_time = datetime.strptime(str(check_in_time), "%Y-%m-%d %H:%M:%S").strftime('%d/%b/%Y %H:%M:%S')
                            
                        if check_out_time :
                            datecheck_out_time = datetime.strptime(str(check_out_time), "%Y-%m-%d %H:%M:%S").strftime('%d/%b/%Y %H:%M:%S')
                    
                    if tot_hours < (current_shift.hours_per_day -1):
                        remarks = 'Half Present'
                    if tot_hours < ((current_shift.hours_per_day)/2):
                        remarks = 'Absent.' 
                    gazetted_color = '0'
                    for gazetted_day in current_shift.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                        gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                        if str(date_after_month.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(date_after_month.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            remarks = str(gazetted_day.name)
                            gazetted_color = '1'
                    leave_color = '0'                    
                    daily_leave = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('request_date_from','<=', date_after_month.strftime('%Y-%m-%d')),('request_date_to','>=', date_after_month.strftime('%Y-%m-%d')),('state','in',('validate','confirm'))]) 
                    if daily_leave:
                        if daily_leave.holiday_status_id.is_rest_day != True: 
                            status = ' '
                            if daily_leave.state == 'confirm':
                                status = 'To Approve'     
                            if daily_leave.state == 'validate':
                                status = 'Approved'         
                            remarks =  str(daily_leave.holiday_status_id.name) +' ('+str(status) +')'        
                            leave_color = '1'
                    rest_schedule_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month),('rest_day','=', True)], limit=1)

                    if rest_schedule_line:
                        rest_day = 'Y'    
                        if datecheck_in_time and datecheck_out_time:
                            remarks = 'Attendance Present.'
                        else:    
                            remarks = 'Restday.'
                    daily_rectify = self.env['hr.attendance.rectification'].sudo().search([('employee_id','=', employee.id),('date','=', date_after_month),('state','in', ('approved','submitted'))], limit=1)
                    if  daily_rectify:
                        remarks =  'Rectification' +' ('+str(daily_rectify.state) +')'    
                    attendances.append({
                            'date': date_after_month.strftime('%d/%b/%Y'),
                            'day':  day1,
                            'check_in': datecheck_in_time,
                            'check_out':  datecheck_out_time,
                            'hours': tot_hours,
                            'shift': shift,
                            'rest_day': rest_day,
                            'leave': leave_color,
                            'gazetted': gazetted_color,
                            'remarks': remarks,
                    })
                else:
                    emp_leaves = self.env['hr.leave'].search([('employee_id','=', employee.id),('request_date_from','=', date_after_month)], limit=1)
                    if emp_leaves:
                        remarks = str(emp_leaves.holiday_status_id.name)
                    else:
                        remarks = 'Absent.'

                    shift = self.env['resource.calendar'].search([], limit=1).name
                    shift = self.env['resource.calendar'].search([('company_id','=', employee.company_id.id)], limit=1).name
                    current_shift = self.env['resource.calendar'].search([], limit=1)
                    current_shift = self.env['resource.calendar'].search([('company_id','=', employee.company_id.id)], limit=1)
                    shift_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month)], limit=1)
                    if shift_line.first_shift_id:
                        shift = shift_line.first_shift_id.name
                        current_shift = shift_line.first_shift_id
                    elif shift_line.second_shift_id:
                        shift = shift_line.second_shift_id.name
                        current_shift = shift_line.second_shift_id

                    rest_schedule_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month),('rest_day','=', True)], limit=1)

                    if rest_schedule_line:
                        rest_day = 'Y'    
                        remarks = 'Restday.'

                    day1 = date_after_month.strftime('%A')    
                    
                    gazetted_color = '0'
                    request_date = date_after_month    
                    for gazetted_day in current_shift.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                        gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                        if str(date_after_month.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(date_after_month.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            remarks = str(gazetted_day.name)
                            gazetted_color = '1'
                            rest_day = 'Y' 
                    check_in_time =  ' '
                    check_out_time = ' '
                    leave_color = '0' 
                    daily_leave = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('request_date_from','<=', date_after_month.strftime('%Y-%m-%d')),('request_date_to','>=', date_after_month.strftime('%Y-%m-%d')),('state','in',('validate','confirm'))]) 
                    if daily_leave:
                        if daily_leave.holiday_status_id.is_rest_day != True: 
                            status = ' '
                            if daily_leave.state == 'confirm':
                                status = 'To Approve'     
                            if daily_leave.state == 'validate':
                                status = 'Approved'         
                            remarks =  str(daily_leave.holiday_status_id.name) +' ('+str(status) +')'
                            leave_color = '1'
                    daily_rectify = self.env['hr.attendance.rectification'].sudo().search([('employee_id','=', employee.id),('date','=', date_after_month),('state','in', ('approved','submitted'))], limit=1)
                    if  daily_rectify:
                        remarks =  'Rectification' +' ('+str(daily_rectify.state) +')' 
                    attendances.append({
                        'date': date_after_month.strftime('%d/%b/%Y'),
                        'day':  day1,
                        'check_in': check_in_time,
                        'check_out':  check_out_time,
                        'hours': 0.0,
                        'shift': shift,
                        'leave': leave_color,
                        'gazetted': gazetted_color,
                        'rest_day': rest_day,
                        'remarks': remarks,
                    })
                    
            employees_attendance.append({
                'name': employee.name,
                'workdays': work_day_line,
                'employee_no': employee.emp_number,
                'attendances': attendances,
            }) 
        
        return {
                'employee': docs,
                'employees_attendance': employees_attendance,
                'date_from': datetime.strptime(str(docs.start_date), "%Y-%m-%d").strftime('%Y-%m-%d'),
                'date_to': datetime.strptime(str(docs.end_date), "%Y-%m-%d").strftime('%Y-%m-%d'),
               }
        


        
# #  portal Report


class PurchaseAttendanceReport(models.AbstractModel):
    _name = 'report.de_hr_attendance_report.attendance_report_portal'
    _description = 'Hr Attendance Report'

    
    
    
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        employees_attendance = []
        portal_employee = []
        portal_employee.append(data['employee'])
        
        for employee11 in portal_employee:
            work_day_line = [] 
            
            employee = self.env['hr.employee'].sudo().search([('id',
                                                       '=', employee11)], limit=1)
            date_from = datetime.strptime(str(data['start_date']), "%Y-%m-%d")
            date_to = datetime.strptime(str(data['end_date']), "%Y-%m-%d")

            work_days = 0
            work_hours = 0 
            
            """
              Employee Attendance Days
            """ 
            emp_attendance = self.env['hr.attendance'].sudo().search([('employee_id','=', employee.id),('att_date','>=', date_from),('att_date','<=', date_to)])
            previous_date = fields.date.today()
            work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','WORK100')], limit=1)
            for attendance in emp_attendance:
                if attendance.check_out and attendance.check_in:
                    new_date = attendance.check_out.strftime('%y-%m-%d')
                    if new_date != previous_date: 
                        daily_leave = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('request_date_from','<=', attendance.att_date),('request_date_to','>=', attendance.att_date),('state','in',('validate','confirm'))]) 
                        if daily_leave.number_of_days == 0.5:
                            work_days += 0.5
                            work_hours += attendance.worked_hours / 2 
                        elif  daily_leave.number_of_days == 0.25:
                            work_days += 0.75
                            att_hours = attendance.worked_hours / 4 
                            work_hours += attendance.worked_hours - att_hours
                        else:     
                            work_days += 1
                            work_hours += attendance.worked_hours
                    previous_date = attendance.check_out.strftime('%y-%m-%d')
            work_day_line.append({
               'work_entry_type_id' : work_entry_type.id ,
               'name': work_entry_type.name ,
               'sequence': work_entry_type.sequence ,
               'number_of_days' : work_days ,
               'number_of_hours' : work_hours ,
            })
                      
            """
              Employee Timoff by Timeoff type wise
            """ 
            
            leave_type = []
            
            total_leave_days = 0
            emp_leaves = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('date_from','>=', date_from),('date_to','<=', date_to),('state','in',('validate','confirm')),('holiday_status_id.is_rest_day','=',False)])
            previous_date = fields.date.today()
            leave_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','LEAVE100')], limit=1)
            for leave in emp_leaves: 
                leave_type.append(leave.holiday_status_id.id)
            uniq_leave_type = set(leave_type)
            for timeoff_type in uniq_leave_type:
                leave_work_days = 0
                leaves_work_hours = 0 
                emp_leaves_type = self.env['hr.leave'].sudo().search([('holiday_status_id','=', timeoff_type),('employee_id','=', employee.id),('date_from','>=', date_from),('date_to','<=', date_to),('state','in',('validate','confirm'))])
                for timeoff in emp_leaves_type:
                    leave_work_days += timeoff.number_of_days
                    total_leave_days += timeoff.number_of_days 
                timeoff_vals = self.env['hr.leave.type'].sudo().search([('id','=',timeoff_type)], limit=1) 
                
                timeoff_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=',timeoff_vals.name)], limit=1)
                if not timeoff_work_entry_type:
                    vals = {
                        'name': timeoff_vals.name,
                        'code': timeoff_vals.name,
                        'round_days': 'NO',
                    }
                    work_entry = self.env['hr.work.entry.type'].sudo().create(vals)
                timeoff_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=',timeoff_vals.name)], limit=1)

                work_day_line.append({
                   'work_entry_type_id' : timeoff_work_entry_type.id,
                   'name': timeoff_work_entry_type.name,
                   'sequence': timeoff_work_entry_type.sequence,
                   'number_of_days' : leave_work_days,
                   'number_of_hours' : leave_work_days * employee.shift_id.hours_per_day ,
                })               
                
            """
              Employee Absent Days
            """ 
            absent_work_days_initial = 0
            delta = date_from - date_to
            total_days = abs(delta.days)
            for i in range(0, total_days + 1):
                absent_work_days_initial = absent_work_days_initial + 1
            rest_days_initial = 0
            gazetted_days_count = 0
            absent_work_days = 0
            shift_contract_lines = self.env['hr.shift.schedule.line'].sudo().search([('employee_id','=', employee.id),('date','>=',date_from),('date','<=',date_to),('state','=','posted')])
            counts = 0
            for shift_line in shift_contract_lines:
                if shift_line.first_shift_id:
                    for gazetted_day in shift_line.first_shift_id.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                        gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                        if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            gattendance = self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=',shift_line.date)])
                            gdaily_leave = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('request_date_from','<=', shift_line.date),('request_date_to','>=', shift_line.date),('state','in',('validate','confirm'))]) 
                            if gattendance:
                                pass
                            elif gdaily_leave:
                                pass
                            else:
                                gazetted_days_count += 1
                else:
                    current_shift = employee.shift_id
                    if not current_shift:
                        current_shift = self.env['resource.calendar'].sudo().search([('company_id','=', employee.company_id.id)], limit=1)
                    if not current_shift:
                        current_shift = self.env['resource.calendar'].sudo().search([], limit=1)

                    for gazetted_day in current_shift.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                        gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                        if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            gattendance = self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=',shift_line.date)])
                            gdaily_leave = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('request_date_from','<=', shift_line.date),('request_date_to','>=', shift_line.date),('state','in',('validate','confirm'))]) 
                            if gattendance:
                                pass
                            elif gdaily_leave:
                                pass
                            else:
                                gazetted_days_count += 1       
                if shift_line.rest_day == True:
                    exist_attendance = self.env['hr.attendance'].search([('employee_id','=',employee.id),('att_date','=',shift_line.date)])
                    if  exist_attendance.check_in and exist_attendance.check_out:
                        pass
                    else:
                        rest_days_initial += 1  
                    if shift_line.first_shift_id:
                        for gazetted_day in shift_line.first_shift_id.global_leave_ids:
                            gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                            gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                            if str(shift_line.date) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                                rest_days_initial -= 1     
                    else:
                        
                        current_shift = self.env['resource.calendar'].sudo().search([], limit=1)
                        current_shift = self.env['resource.calendar'].sudo().search([('company_id','=', employee.company_id.id)], limit=1)
                        for gazetted_day in current_shift.global_leave_ids:
                            gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                            gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                            if str(shift_line.date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(shift_line.date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                                rest_days_initial -= 1 
                        
                                   
            work_day_line.append({
                   'work_entry_type_id' : 1,
                   'name': 'Gazetted Holidays',
                   'sequence': 2,
                   'number_of_days' : gazetted_days_count,
                   'number_of_hours' : gazetted_days_count * employee.shift_id.hours_per_day ,
            })   
            
            """
              Rest Day 
            """
            rest_day_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','Rest Day')], limit=1)
            
            if not rest_day_work_entry_type:
                vals = {
                    'name': 'Rest Day',
                    'code': 'Rest Day',
                    'round_days': 'NO',
                }
                work_entry = self.env['hr.work.entry.type'].sudo().create(vals)  
            rest_day_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','Rest Day')], limit=1)    
            work_day_line.append({
               'work_entry_type_id' : rest_day_work_entry_type.id,
               'name': rest_day_work_entry_type.name,
               'sequence': rest_day_work_entry_type.sequence,
               'number_of_days' : rest_days_initial ,
               'number_of_hours' : rest_days_initial * employee.shift_id.hours_per_day ,
            })
            absent_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','ABSENT100')], limit=1)
            if not absent_work_entry_type:
                vals = {
                    'name': 'Absent Days',
                    'code': 'ABSENT100',
                    'round_days': 'NO',
                }
                work_entry = self.env['hr.work.entry.type'].sudo().create(vals)
            apply_leave_days = 0    
            emp_leaves_apply = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('date_from','>=', date_from),('date_to','<=', date_to),('state','=','validate')]) 
            for leave_apply in emp_leaves_apply:
                apply_leave_days += leave_apply.number_of_days
            
            absent_work_days = absent_work_days_initial - (gazetted_days_count + rest_days_initial + total_leave_days + work_days)
            absent_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code','=','ABSENT100')], limit=1)
            
            work_day_line.append({
               'work_entry_type_id' : absent_work_entry_type.id,
               'name': absent_work_entry_type.name,
               'sequence': absent_work_entry_type.sequence,
               'number_of_days' : absent_work_days  if absent_work_days >0.0 else 0,
               'number_of_hours' : (absent_work_days if absent_work_days >0.0 else 0) * employee.shift_id.hours_per_day ,
            })
            


    
            attendances = []
            delta = date_from - date_to
            total_days = abs(delta.days)
            rest_day_count = 0
            for i in range(0, total_days + 1):            
                day = ' '
                remarks = ' '
                rest_day = 'N'                    

                date_after_month = date_from + relativedelta(days=i)

                hr_attendance = self.env['hr.attendance'].search([('employee_id','=', employee.id),('att_date','=', date_after_month)]) 
                if hr_attendance:
                    datecheck_in_time  = ' '
                    datecheck_out_time = ' '
                    day1 = date_after_month.strftime('%A')
                    shift = employee.shift_id.name
                    tot_hours = 0
                    rest_day = 'N'
                    remarks = ' '
                    current_shift = employee.shift_id
                    for attendance in hr_attendance:
                        tot_hours +=  attendance.worked_hours
                        emp_leaves = self.env['hr.leave'].search([('employee_id','=', employee.id),('request_date_from','=', date_after_month)], limit=1)
                        shift = attendance.shift_id.name
                        if not shift:
                            shift = attendance.employee_id.shift_id.name
                        current_shift = attendance.shift_id
                        if  attendance.check_out and attendance.check_in:
                            remarks = 'Attendance Present.'
                        elif not attendance.check_out and attendance.check_in:
                            remarks = 'Check Out is Missing' 
                        elif not attendance.check_in and attendance.check_out: 
                            remarks = 'Check In is Missing'
                        elif emp_leaves:
                            remarks = str(emp_leaves.holiday_status_id.name)
                        else:
                            remarks = 'Absent.'
                        if not  shift:   
                            shift = self.env['resource.calendar'].search([], limit=1).name
                            shift = self.env['resource.calendar'].search([('company_id','=', employee.company_id.id)], limit=1).name
                            current_shift = self.env['resource.calendar'].search([], limit=1)
                            current_shift = self.env['resource.calendar'].search([('company_id','=', employee.company_id.id)], limit=1)
                            shift_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month)], limit=1)
                            if shift_line.first_shift_id:
                                shift = shift_line.first_shift_id.name
                                current_shift = attendance.shift_id
                            elif shift_line.second_shift_id:
                                shift = shift_line.second_shift_id.name
                                current_shift = attendance.shift_id

                        rest_schedule_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month),('rest_day','=', True)], limit=1)

                        if rest_schedule_line:
                            rest_day = 'Y'    
                            remarks = 'Restday.'
                            rest_day_count += 1 


                        day1 = date_after_month.strftime('%A')    

                        check_in_time =  attendance.check_in
                        check_out_time = attendance.check_out
                        if  attendance.check_in:
                            check_in_time = attendance.check_in + relativedelta(hours =+ 5)

                        if  attendance.check_out:
                            check_out_time = attendance.check_out + relativedelta(hours =+ 5)
                        datecheck_in_time = check_in_time
                        datecheck_out_time = check_out_time
                        if check_in_time :
                            datecheck_in_time = datetime.strptime(str(check_in_time), "%Y-%m-%d %H:%M:%S").strftime('%d/%b/%Y %H:%M:%S')
                            
                        if check_out_time :
                            datecheck_out_time = datetime.strptime(str(check_out_time), "%Y-%m-%d %H:%M:%S").strftime('%d/%b/%Y %H:%M:%S')
                            
                            
                    if tot_hours < (current_shift.hours_per_day -1):
                        remarks = 'Half Present'
                    if tot_hours < ((current_shift.hours_per_day)/2):
                        remarks = 'Absent.'
                    gazetted_color = '0'    
                    for gazetted_day in current_shift.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                        gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                        if str(date_after_month.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(date_after_month.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            remarks = str(gazetted_day.name)
                            gazetted_color = '1'    
                    leave_color = '0'    
                    daily_leave = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('request_date_from','<=', date_after_month.strftime('%Y-%m-%d')),('request_date_to','>=', date_after_month.strftime('%Y-%m-%d')),('state','in',('validate','confirm'))]) 
                    if daily_leave:
                        if daily_leave.holiday_status_id.is_rest_day != True: 
                            status = ' '
                            if daily_leave.state == 'confirm':
                                status = 'To Approve'     
                            if daily_leave.state == 'validate':
                                status = 'Approved'         
                            remarks =  str(daily_leave.holiday_status_id.name) +' ('+str(status) +')'          
                            leave_color = '1'
                    rest_schedule_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month),('rest_day','=', True)], limit=1)

                    if rest_schedule_line:
                        rest_day = 'Y'
                        if datecheck_in_time and datecheck_out_time:
                            remarks = 'Attendance Present.'
                        else:    
                            remarks = 'Restday.'
                    daily_rectify = self.env['hr.attendance.rectification'].sudo().search([('employee_id','=', employee.id),('date','=', date_after_month),('state','in', ('approved','submitted'))], limit=1)
                    if  daily_rectify:
                        remarks =  'Rectification' +' ('+str(daily_rectify.state) +')' 
                    attendances.append({
                            'date': date_after_month.strftime('%d/%b/%Y'),
                            'day':  day1,
                            'check_in': datecheck_in_time,
                            'check_out':  datecheck_out_time,
                            'hours': tot_hours,
                            'leave': leave_color,
                            'gazetted': gazetted_color,
                            'shift': shift,
                            'rest_day': rest_day,
                            'remarks': remarks,
                    })
                else:
                    emp_leaves = self.env['hr.leave'].search([('employee_id','=', employee.id),('request_date_from','=', date_after_month)], limit=1)
                    if emp_leaves:
                        remarks = str(emp_leaves.holiday_status_id.name)
                    else:
                        remarks = 'Absent.'

                    shift = self.env['resource.calendar'].search([], limit=1).name
                    shift = self.env['resource.calendar'].search([('company_id','=', employee.company_id.id)], limit=1).name
                    current_shift = self.env['resource.calendar'].search([], limit=1)
                    current_shift = self.env['resource.calendar'].search([('company_id','=', employee.company_id.id)], limit=1)
                    shift_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month)], limit=1)
                    if shift_line.first_shift_id:
                        shift = shift_line.first_shift_id.name
                        current_shift = shift_line.first_shift_id
                    elif shift_line.second_shift_id:
                        shift = shift_line.second_shift_id.name
                        current_shift = shift_line.second_shift_id

                    rest_schedule_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month),('rest_day','=', True)], limit=1)

                    if rest_schedule_line:
                        rest_day = 'Y'    
                        remarks = 'Restday.'

                    day1 = date_after_month.strftime('%A')    
                    
                    gazetted_color = '0'
                    request_date = date_after_month    
                    for gazetted_day in current_shift.global_leave_ids:
                        gazetted_date_from = gazetted_day.date_from +relativedelta(hours=+5)
                        gazetted_date_to = gazetted_day.date_to +relativedelta(hours=+5)
                        if str(date_after_month.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(date_after_month.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                            remarks = str(gazetted_day.name)
                            gazetted_color = '1'
                            rest_day = 'Y' 
                    check_in_time =  ' '
                    check_out_time = ' '
                    leave_color = '0'
                    daily_leave = self.env['hr.leave'].sudo().search([('employee_id','=', employee.id),('request_date_from','<=', date_after_month.strftime('%Y-%m-%d')),('request_date_to','>=', date_after_month.strftime('%Y-%m-%d')),('state','in',('validate','confirm'))]) 
                    if daily_leave:
                        if daily_leave.holiday_status_id.is_rest_day != True: 
                            status = ' '
                            if daily_leave.state == 'confirm':
                                status = 'To Approve'     
                            if daily_leave.state == 'validate':
                                status = 'Approved'         
                            remarks =  str(daily_leave.holiday_status_id.name) +' ('+str(status) +')' 
                            leave_color = '1'
                    daily_rectify = self.env['hr.attendance.rectification'].sudo().search([('employee_id','=', employee.id),('date','=', date_after_month),('state','in', ('approved','submitted'))], limit=1)
                    if  daily_rectify:
                        remarks =  'Rectification' +' ('+str(daily_rectify.state) +')' 
                    attendances.append({
                        'date': date_after_month.strftime('%d/%b/%Y'),
                        'day':  day1,
                        'check_in': check_in_time,
                        'check_out':  check_out_time,
                        'hours': 0.0,
                        'shift': shift,
                        'leave': leave_color,
                        'gazetted': gazetted_color,
                        'rest_day': rest_day,
                        'remarks': remarks,
                    })
                    
            employees_attendance.append({
                'name': employee.name,
                'workdays': work_day_line,
                'employee_no': employee.emp_number,
                'attendances': attendances,
            }) 
        
        return {
                'employees_attendance': employees_attendance,
                'date_from': datetime.strptime(str(data['start_date']), "%Y-%m-%d").strftime('%Y-%m-%d'),
                'date_to': datetime.strptime(str(data['end_date']), "%Y-%m-%d").strftime('%Y-%m-%d'),
               }
        
        
        