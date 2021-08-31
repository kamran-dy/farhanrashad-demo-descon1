# -*- coding: utf-8 -*-

import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    

    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        for payslip in self:
            for rule in payslip.line_ids:
    #                 rule_code = 'COST1'
                cost_amount = 0
                contract = self.env['hr.contract'].search([('employee_id','=',payslip.employee_id.id),('state','=','open')],limit=1)
                for cost_line in contract.cost_center_information_line:
                    if cost_line.cost_center_id.id == rule.salary_rule_id.analytic_account_id.id:
                        if rule.salary_rule_id.account_debit:
                            if cost_line.main_account_id.code[0:4] == rule.salary_rule_id.account_debit.code[0:4]:
        #                     rule_code =  cost_line.cost_center.code 
        #                     for inner_rule in self.line_ids:
                                if rule.category_id.name in ['Basic_month','Allowance','Contribution Exp']:
                                    cost_amount = (((cost_line.percentage_charged_cost_center / 100) * rule.amount) * (cost_line.percentage_charged / 100))
                                    rule.update({
                                        'amount': cost_amount,
                                        'cost_divided': True
                                    })
                        else:
                            if rule.category_id.name in ['Basic_month','Allowance','Contribution Exp']:
                                cost_amount = (((cost_line.percentage_charged_cost_center / 100) * rule.amount) * (cost_line.percentage_charged / 100))
                                rule.update({
                                    'amount': cost_amount,
                                    'cost_divided': True
                                })
            for rule in payslip.line_ids:
                if rule.cost_divided == False:
                    contract = self.env['hr.contract'].search([('employee_id','=',payslip.employee_id.id),('state','=','open')],limit=1)
                    for cost_line in contract.cost_center_information_line:

#                         if cost_line.cost_center_id.id != rule.salary_rule_id.analytic_account_id.id:
                        if rule.category_id.name in ['Basic_month','Allowance','Contribution Exp']:
                            rule.update({
                                'amount': 0
                            })
            for rule in payslip.line_ids:
                if rule.amount == 0.0:
                    rule.unlink()    

            total_basic = 0
            total_allowance = 0
            total_deduction = 0
            total_compensation = 0
            total_gross = 0
            amount_total = 0
            amount_exceed = 0
            for rule in payslip.line_ids:
                if rule.category_id.name == 'Basic_month':
                    total_basic = rule.total + total_basic
                if rule.category_id.name == 'Allowance':
                    total_allowance = rule.total + total_allowance
                if rule.category_id.name == 'Deduction':
                    total_deduction = rule.total + total_deduction
                if rule.category_id.name == 'Compensation':
                    total_compensation = rule.total + total_compensation
            for rule in payslip.line_ids:
                if rule.category_id.code == 'GROSS':
                    rule.update({
                        'amount': total_basic + total_allowance + total_compensation
                    })
                    total_gross = total_basic + total_allowance + total_compensation
                
                if rule.category_id.code == 'INC01':
                    
                    if ((total_gross)*12>=600001 and (total_gross)*12<=1200000):result = -(round(((((total_gross*12)-600000)/100)*5)/12,0))
                    elif ((total_gross)*12>=1200001 and (total_gross)*12<=1800000):result = -(round((((((categories.GROSS*12)-1200000)/100)*10)+30000)/12,0))
                    elif ((total_gross)*12>=1800001 and (total_gross)*12<=2500000):result = -(round((((((total_gross*12)-1800000)/100)*15)+90000)/12,0))
                    elif ((total_gross)*12>=2500001 and (total_gross)*12<=3500000):result = -(round((((((total_gross*12)-2500000)/100)*17.5)+195000)/12,0))
                    elif ((total_gross)*12>=3500001 and (total_gross)*12<=5000000):result = -(round((((((total_gross*12)-3500000)/100)*20)+370000)/12,0))
                    elif ((total_gross)*12>=5000001 and (total_gross)*12<=8000000):result = -(round((((((total_gross*12)-5000000)/100)*22.5)+670000)/12,0))
                    elif ((total_gross)*12>=8000001 and (total_gross)*12<=12000000):result = -(round((((((total_gross*12)-8000000)/100)*25)+1345000)/12,0))
                    elif ((total_gross)*12>=12000001 and (total_gross)*12<=30000000):result = -(round((((((total_gross*12)-12000000)/100)*27.5)+2345000)/12,0))
                    elif ((total_gross)*12>=30000001 and (total_gross)*12<=50000000):result = -(round((((((total_gross*12)-30000000)/100)*30)+7295000)/12,0))
                    elif ((total_gross)*12>=50000001 and (total_gross)*12<=75000000):result = -(round((((((total_gross*12)-50000000)/100)*32.5)+13295000)/12,0))
                    elif ((total_gross)*12>=75000001):result = -(round((((((total_gross*12)-75000000)/100)*35)+21420000)/12,0))
                    else:result = 0.0
                    
                    rule.update({
                        'amount': result
                    })
                
                if rule.category_id.code == 'PFT01':
                    amount_exceed = (((round(((contract.wage/100)*6.3),2))*12) - 150000)
                    amount_total = total_gross + amount_exceed


                    if ((amount_total)*12>=600001 and (amount_total)*12<=1200000):result = (-(round(((((amount_total*12)-600000)/100)*5)/12,0))+(round(((((total_gross*12)-600000)/100)*5)/12,0)))
                    elif ((amount_total)*12>=1200001 and (amount_total)*12<=1800000):result = (-(round((((((amount_total*12)-1200000)/100)*10)+30000)/12,0))+(round((((((total_gross*12)-1200000)/100)*10)+30000)/12,0)))
                    elif ((amount_total)*12>=1800001 and (amount_total)*12<=2500000):result = (-(round((((((amount_total*12)-1800000)/100)*15)+90000)/12,0))+(round((((((total_gross*12)-1800000)/100)*15)+90000)/12,0)))
                    elif ((amount_total)*12>=2500001 and (amount_total)*12<=3500000):result = (-(round((((((amount_total*12)-2500000)/100)*17.5)+195000)/12,0))+(round((((((total_gross*12)-2500000)/100)*17.5)+195000)/12,0)))
                    elif ((amount_total)*12>=3500001 and (amount_total)*12<=5000000):result = (-(round((((((amount_total*12)-3500000)/100)*20)+370000)/12,0))+(round((((((total_gross*12)-3500000)/100)*20)+370000)/12,0)))
                    elif ((amount_total)*12>=5000001 and (amount_total)*12<=8000000):result = (-(round((((((amount_total*12)-5000000)/100)*22.5)+670000)/12,0))+(round((((((total_gross*12)-5000000)/100)*22.5)+670000)/12,0)))
                    elif ((amount_total)*12>=8000001 and (amount_total)*12<=12000000):result = (-(round((((((amount_total*12)-8000000)/100)*25)+1345000)/12,0))+(round((((((total_gross*12)-8000000)/100)*25)+1345000)/12,0)))
                    elif ((amount_total)*12>=12000001 and (amount_total)*12<=30000000):result = (-(round((((((amount_total*12)-12000000)/100)*27.5)+2345000)/12,0))+(round((((((total_gross*12)-12000000)/100)*27.5)+2345000)/12,0)))
                    elif ((amount_total)*12>=30000001 and (amount_total)*12<=50000000):result = (-(round((((((amount_total*12)-30000000)/100)*30)+7295000)/12,0))+(round((((((total_gross*12)-30000000)/100)*30)+7295000)/12,0)))
                    elif ((amount_total)*12>=50000001 and (amount_total)*12<=75000000):result = (-(round((((((amount_total*12)-50000000)/100)*32.5)+13295000)/12,0))+(round((((((total_gross*12)-50000000)/100)*32.5)+13295000)/12,0)))
                    elif ((amount_total)*12>=75000001):result = (-(round((((((amount_total*12)-75000000)/100)*35)+21420000)/12,0))+(round((((((total_gross*12)-75000000)/100)*35)+21420000)/12,0)))
                    else:result = 0.0
                
                    rule.update({
                        'amount': result
                    })
                
                
            total_basic = 0
            total_allowance = 0
            total_deduction = 0
            total_compensation = 0    
            for rule in payslip.line_ids:
                if rule.category_id.name == 'Basic_month':
                    total_basic = rule.total + total_basic
                if rule.category_id.name == 'Allowance':
                    total_allowance = rule.total + total_allowance
                if rule.category_id.name == 'Deduction':
                    total_deduction = rule.total + total_deduction
                if rule.category_id.name == 'Compensation':
                    total_compensation = rule.total + total_compensation
                    
            for rule in payslip.line_ids:
                
                if rule.category_id.code == 'NET':
                    rule.update({
                        'amount': total_basic + total_allowance + total_compensation + total_deduction
                    })

        return res



class HrPayslipline(models.Model):
    _inherit = 'hr.payslip.line'
    
    cost_divided = fields.Boolean(String="Cost Divided")
    

