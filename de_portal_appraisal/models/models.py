# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class de_portal_appraisal(models.Model):
#     _name = 'de_portal_appraisal.de_portal_appraisal'
#     _description = 'de_portal_appraisal.de_portal_appraisal'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
