# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrPayrollAttendance(http.Controller):
#     @http.route('/de_hr_payroll_attendance/de_hr_payroll_attendance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_payroll_attendance/de_hr_payroll_attendance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_payroll_attendance.listing', {
#             'root': '/de_hr_payroll_attendance/de_hr_payroll_attendance',
#             'objects': http.request.env['de_hr_payroll_attendance.de_hr_payroll_attendance'].search([]),
#         })

#     @http.route('/de_hr_payroll_attendance/de_hr_payroll_attendance/objects/<model("de_hr_payroll_attendance.de_hr_payroll_attendance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_payroll_attendance.object', {
#             'object': obj
#         })
