# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PortalAppraisal(models.Model):
    _inherit = 'hr.appraisal.feedback'
    

class ResCompany(models.Model):
    _inherit = 'res.company'    
    
