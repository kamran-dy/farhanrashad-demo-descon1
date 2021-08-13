from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EmployeeType(models.Model):
    _name = 'employee.type'
    _description = 'Employee Type'
    
    name = fields.Char(string="Employee Type")