# # -*- coding: utf-8 -*-

from . import config
from . import update
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import OrderedDict
from operator import itemgetter
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR
import ast
appraisal_objective_list = []
halfyear_objective_list = []

def appraisal_page_content(flag = 0):
    global appraisal_objective_list 
    managers = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    return {
        'managers': managers,
        'employees' : employees,
        'appraisal_objective_list': appraisal_objective_list,
        'success_flag' : flag,
        'company_info': company_info,
    }

def paging(data, flag1 = 0, flag2 = 0):        
    if flag1 == 1:
        return config.list12
    elif flag2 == 1:
        config.list12.clear()
    else:
        k = []
        for rec in data:
            for ids in rec:
                config.list12.append(ids.id)        
        
class CreateAppraisal(http.Controller):
    
    @http.route('/appraisal/objective/create/',type="http", website=True, auth='user')
    def appraisal_objective_template(self, **kw):
        global appraisal_objective_list
        appraisal_objective_list = []
        return request.render("de_portal_appraisal.create_appraisal_objective",appraisal_page_content()) 
    
    
    @http.route('/halfyear/feedback/objective/edit/',type="http", website=True, auth='user')
    def halfyear_feedback_objective_template(self, **kw):
        global halfyear_objective_list
        halfyear_objective_list = []
        return request.render("de_portal_appraisal.edit_feedback_objective",appraisal_page_content()) 
    
    
    @http.route('/objective/line/save',type="http", website=True, auth='user')
    def objective_line_template(self, **kw):
        objectiveline = request.env['hr.appraisal.objective'].search([('id', '=', kw.get('objective_id'))])
        objective_list = ast.literal_eval(kw.get('objective_vals'))
        obj_count = 0
        for obj_line in objective_list:
            obj_count += 1
            if obj_count > 1 :               
                objective_line = request.env['hr.appraisal.objective.line'].search([('id', '=', obj_line['col1'])])
                if objective_line:
                    objective_line.update({
                        'objective': obj_line['col4'],
                        'weightage': obj_line['col2'],
                        'priority':  obj_line['col3'],
                    })
        return request.redirect('/appraisal/objective/%s'%(objectiveline.id))        
    
    
    
    @http.route('/feedback/line/save', type="http", auth="public", website=True)
    def feedback_line(self, **kw):
        feedbackuser = request.env['hr.appraisal.feedback'].search([('id', '=', kw.get('docuid'))])
        if feedbackuser.state == 'sent' and  feedbackuser.name.user_id.id ==  http.request.env.context.get('uid'):
            feedbackuser.update({
                'reason_for_disagreement':  kw.get('reason_for_disagreement'),
                'agreement': kw.get('agreement'),
            })
        elif feedbackuser.state == 'draft':
            feedbackuser.update({
                'objective_comment': kw.get('objective_comment'),
                'value_comment': kw.get('value_comment'),
            })
            
        if feedbackuser.state == 'end_year_sent_emp_view' and  feedbackuser.name.user_id.id ==  http.request.env.context.get('uid'):
            feedbackuser.update({
                'full_year_agreement':  kw.get('full_year_agreement'),
                'full_reason_for_disagreement': kw.get('full_reason_for_disagreement'),
            })    
            
        if feedbackuser.state == 'draft':    
            user_business_obj = ast.literal_eval(kw.get('lista'))
            user_core_object = ast.literal_eval(kw.get('user_core_vals_list'))
            final_count = 0
            for appraisee_line in user_business_obj:
                final_count += 1

            core_count = 0
            for core_line in user_core_object:
                core_count = core_count + 1
                if core_count > 1 :               
                    acore_objective = request.env['hr.appraisal.feedback.values.appraisee.line'].search([('id', '=', core_line['col1'])])
                    if acore_objective:
                        acore_objective.update({
                            'conformance_level': core_line['col2'],
                            'remarks': core_line['col3'],
                        })
            count = 0
            for appraisee_line in user_business_obj:
                count = count + 1
                if count > 1 and count <= (final_count):               
                    appraisee_objective = request.env['hr.appraisal.feedback.objective.appraisee.line'].search([('id', '=', appraisee_line['col1'])])
                    if appraisee_objective:
                        appraisee_objective.update({
                            'remarks': appraisee_line['col2'],
                            'percentage_score': appraisee_line['col3'],
                        })
                        
        elif feedbackuser.state == 'confirm': 
            feedbackmanger = request.env['hr.appraisal.feedback'].search([('id', '=', kw.get('docuid'))])
            if feedbackmanger:
                feedbackmanger.update({
                    'full_year_value_comment': kw.get('full_year_value_comment'),
                    'full_year_objective_comment': kw.get('full_year_objective_comment'),
                })
            manager_business_obj = ast.literal_eval(kw.get('listb'))
            manager_core_object = ast.literal_eval(kw.get('manager_core_vals_list'))
            mfinal_count = 0
            for eappraisee_line in manager_business_obj:
                mfinal_count += 1

            cmore_count = 0
            if manager_core_object:
                for mcore_line in manager_core_object:
                    cmore_count = cmore_count + 1
                    if cmore_count > 1 :               
                        macore_objective = request.env['hr.appraisal.feedback.values.appraisee.line'].search([('id', '=', mcore_line['col1'])])
                        if macore_objective:
                            macore_objective.update({
                                'remarks_mngr': mcore_line['col3'],
                            })
                            if  mcore_line['col2'] != '0':
                                macore_objective.update({
                                    'conformance_level_mngr': mcore_line['col2'],
                                    'remarks_mngr': mcore_line['col3'],
                                })
                                
            mcount = 0
            for mappraisee_line in manager_business_obj:
                mcount = mcount + 1
                if mcount > 1:               
                    mappraisee_objective = request.env['hr.appraisal.feedback.objective.appraisee.line'].search([('id', '=', mappraisee_line['col1'])])
                    if mappraisee_objective:
                        mappraisee_objective.update({
                            'remarks_mngr': mappraisee_line['col2'],
                            'percentage_score_mngr': mappraisee_line['col3'],
                        })
            
        elif feedbackuser.state == 'sent' and  feedbackuser.name.parent_id.user_id.id ==  http.request.env.context.get('uid'): 
            feedbackmanger = request.env['hr.appraisal.feedback'].search([('id', '=', kw.get('docuid'))])
            if feedbackmanger:
                feedbackmanger.update({
                    'full_year_value_comment': kw.get('full_year_value_comment'),
                    'full_year_objective_comment': kw.get('full_year_objective_comment'),
                })
            manager_business_obj = ast.literal_eval(kw.get('listb'))
            manager_core_object = ast.literal_eval(kw.get('manager_core_vals_list'))
            mfinal_count = 0
            for eappraisee_line in manager_business_obj:
                mfinal_count += 1

            cmore_count = 0
            if manager_core_object:
                for mcore_line in manager_core_object:
                    cmore_count = cmore_count + 1
                    if cmore_count > 1 :               
                        macore_objective = request.env['hr.appraisal.feedback.values.appraisee.line'].search([('id', '=', mcore_line['col1'])])
                        if macore_objective:
                            macore_objective.update({
                                'remarks_mngr': mcore_line['col3'],
                            })
                            if  mcore_line['col2'] != '0':
                                macore_objective.update({
                                    'conformance_level_mngr': mcore_line['col2'],
                                    'remarks_mngr': mcore_line['col3'],
                                })
                                
            mcount = 0
            for mappraisee_line in manager_business_obj:
                mcount = mcount + 1
                if mcount > 1:               
                    mappraisee_objective = request.env['hr.appraisal.feedback.objective.appraisee.line'].search([('id', '=', mappraisee_line['col1'])])
                    if mappraisee_objective:
                        mappraisee_objective.update({
                            'remarks_mngr': mappraisee_line['col2'],
                            'percentage_score_mngr': mappraisee_line['col3'],
                        })                    
                                
        elif feedbackuser.state == 'end_year_appraisee_review': 
            fullfeedbackuser = request.env['hr.appraisal.feedback'].search([('id', '=', kw.get('docuid'))])
            if fullfeedbackuser:
                fullfeedbackuser.update({
                    'half_year_appraiser_objective_comment': kw.get('half_year_appraiser_objective_comment'),
                    'half_year_appraiser_value_comment': kw.get('half_year_appraiser_value_comment'),
                })
            fulluser_business_obj = ast.literal_eval(kw.get('listaa'))
            fulluser_core_object = ast.literal_eval(kw.get('full_user_core_vals_list'))
            fullufinal_count = 0
            for fulluappraisee_line in fulluser_business_obj:
                fullufinal_count += 1

            ucmore_count = 0
            for fullucore_line in fulluser_core_object:
                ucmore_count = ucmore_count + 1
                if ucmore_count > 1 :               
                    fulluacore_objective = request.env['hr.appraisal.feedback.values.line'].search([('id', '=', fullucore_line['col1'])])
                    if fulluacore_objective:
                        fulluacore_objective.update({
                            'rating': fullucore_line['col2'],
                            'full_remarks': fullucore_line['col3'],
                        })
                       
            fullucount = 0
            for fulluappraisee_line in fulluser_business_obj:
                fullucount = fullucount + 1
                if fullucount > 1:               
                    fulluappraisee_objective = request.env['hr.appraisal.feedback.objective.line'].search([('id', '=', fulluappraisee_line['col1'])])
                    if fulluappraisee_objective:
                        fulluappraisee_objective.update({
                            'full_remarks': fulluappraisee_line['col2'],
                            'rating': fulluappraisee_line['col3'],
                        })  
                        
                        
        elif feedbackuser.state == 'end_year_appraiser_review': 
            fullfeedbackmanger = request.env['hr.appraisal.feedback'].search([('id', '=', kw.get('docuid'))])
            if fullfeedbackmanger:
                fullfeedbackmanger.update({
                    'full_year_appraiser_value_comment': kw.get('full_year_appraiser_value_comment'),
                    'full_year_appraiser_objective_comment': kw.get('full_year_appraiser_objective_comment'),
                    'strength_1': kw.get('strength_1'),
                    'strength_2': kw.get('strength_2'),
                    'strength_3': kw.get('strength_3'),
                    'strength_4': kw.get('strength_4'),
                    'strength_5': kw.get('strength_5'),
                    'improvements_1': kw.get('improvements_1'),
                    'improvements_2': kw.get('improvements_2'),
                    'improvements_3': kw.get('improvements_3'),
                    'improvements_4': kw.get('improvements_4'),
                    'improvements_5': kw.get('improvements_5'),
                    'training_1': kw.get('training_1'),
                    'training_2': kw.get('training_2'),
                    'training_3': kw.get('training_3'),
                    'training_4': kw.get('training_4'),
                    'training_5': kw.get('training_5'),
                    'reason_1': kw.get('reason_1'),
                    'reason_2': kw.get('reason_2'),
                    'reason_3': kw.get('reason_3'),
                    'reason_4': kw.get('reason_4'),
                    'reason_5': kw.get('reason_5'),
                    'recommend_promotion': kw.get('recommend_promotion'),
                    'promotion_position': kw.get('promotion_position'),
                    'promotion_grade': kw.get('promotion_grade'),
                     'date_effective': kw.get('date_effective'),
                    
                })
            fullmanager_business_obj = ast.literal_eval(kw.get('listbb'))
            fullmanager_core_object = ast.literal_eval(kw.get('full_manager_core_vals_list'))
            fullmfinal_count = 0
            for fullappraisee_line in fullmanager_business_obj:
                fullmfinal_count += 1

            fullyearm_count = 0
            for fullmcore_line in fullmanager_core_object:
                fullyearm_count +=  + 1
                if fullyearm_count > 1 :               
                    fullmacore_objective = request.env['hr.appraisal.feedback.values.line'].search([('id', '=', fullmcore_line['col1'])])
                    if fullmacore_objective:
                        fullmacore_objective.update({
                            'rating_mngr': fullmcore_line['col3'],
                            'full_remarks_mngr': fullmcore_line['col2'],
                        })
                       
            fullmcount = 0
            for fullmappraisee_line in fullmanager_business_obj:
                fullmcount = fullmcount + 1
                if fullmcount > 1:               
                    fullmappraisee_objective = request.env['hr.appraisal.feedback.objective.line'].search([('id', '=', fullmappraisee_line['col1'])])
                    if fullmappraisee_objective:
                        fullmappraisee_objective.update({
                            'full_remarks_mngr': fullmappraisee_line['col2'],
                            'rating_mngr': fullmappraisee_line['col3'],
                        })  
                        
        elif feedbackuser.state == 'end_year_sent_emp_view' and feedbackuser.name.parent_id.user_id.id == http.request.env.context.get('uid'): 
            fullfeedbackmanger = request.env['hr.appraisal.feedback'].search([('id', '=', kw.get('docuid'))])
            if fullfeedbackmanger:
                fullfeedbackmanger.update({
                    'full_year_appraiser_value_comment': kw.get('full_year_appraiser_value_comment'),
                    'full_year_appraiser_objective_comment': kw.get('full_year_appraiser_objective_comment'),
                })
            fullmanager_business_obj = ast.literal_eval(kw.get('listbb'))
            fullmanager_core_object = ast.literal_eval(kw.get('full_manager_core_vals_list'))
            fullmfinal_count = 0
            for fullappraisee_line in fullmanager_business_obj:
                fullmfinal_count += 1

            fullyearm_count = 0
            for fullmcore_line in fullmanager_core_object:
                fullyearm_count +=  + 1
                if fullyearm_count > 1 :               
                    fullmacore_objective = request.env['hr.appraisal.feedback.values.line'].search([('id', '=', fullmcore_line['col1'])])
                    if fullmacore_objective:
                        fullmacore_objective.update({
                            'rating_mngr': fullmcore_line['col3'],
                            'full_remarks_mngr': fullmcore_line['col2'],
                        })
                       
            fullmcount = 0
            for fullmappraisee_line in fullmanager_business_obj:
                fullmcount = fullmcount + 1
                if fullmcount > 1:               
                    fullmappraisee_objective = request.env['hr.appraisal.feedback.objective.line'].search([('id', '=', fullmappraisee_line['col1'])])
                    if fullmappraisee_objective:
                        fullmappraisee_objective.update({
                            'full_remarks_mngr': fullmappraisee_line['col2'],
                            'rating_mngr': fullmappraisee_line['col3'],
                        })                                  
        
        return request.redirect('/appraisal/feedback/%s'%(feedbackuser.id))
    
    
    
    @http.route('/appraisal/objective/save', type="http", auth="public", website=True)
    def edit_objective(self, **kw):
        obj_line = []
        global appraisal_objective_list
        for worker in appraisal_objective_list:
            obj_line.append((0,0,{
                'objective':  worker['objective'],
                'weightage':  worker['weightage'],
                'priority': worker['priority'],
                }))
        objective_val = {
            'description': kw.get('description'),
            'employee_id': int(kw.get('employee_id')),
            'objective_year': kw.get('objective_year'),
            'objective_lines': obj_line,
        }
        record = request.env['hr.appraisal.objective'].sudo().create(objective_val)
        record.action_sent_review()
        appraisal_objective_list = []
        return request.render("de_portal_appraisal.appraisal_submited", {})
    
    
    
    @http.route('/appraisal/create/',type="http", website=True, auth='user')
    def appraisal_template(self, **kw):
        global appraisal_objective_list
        appraisal_objective_list = []
        return request.render("de_portal_appraisal.portal_appraisal",appraisal_page_content()) 
    
 
    
    
    
    @http.route('/appraisal/objective/line/save', type="http", auth="public", website=True)
    def create_sheet_expense_line(self, **kw):
        global appraisal_objective_list
        appraisal_val = {
            'objective': kw.get('objective'),
            'weightage':  kw.get('weightage'),
            'priority': kw.get('priority'),
           
        }
        appraisal_objective_list.append(appraisal_val)
        return request.render("de_portal_appraisal.create_appraisal_objective",appraisal_page_content())
    
    
  

class CustomerPortal(CustomerPortal):
    
    
    @http.route(['/action/confirm/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_confirm(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_confirm()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    @http.route(['/action/confirm/objective/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_confirm_objective(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.objective'].sudo().browse(id)

        record.action_submit()
        try:
            obj_sudo = self._document_check_access('hr.appraisal.objective', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._appraisal_get_page_view_values(obj_sudo, **kw) 
        return request.redirect('/appraisal/objective/%s'%(record.id))
    
    @http.route(['/action/sent/hr/review/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_Sent_for_Employee_Review(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_Sent_for_Employee_Review()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    @http.route(['/action/endorsed/hr/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_endorsed_employee(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_endorsed_employee()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    @http.route(['/action/endorsed/hr/hod/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_endorsed_hod(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_endorsed_hod()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    
    @http.route(['/action/appraiser/review/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_end_year_appraiser_review(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_end_year_appraiser_review()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    @http.route(['/action/end/appraiser/review/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_end_year_sent_emp_view(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_end_year_sent_emp_view()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    
    @http.route(['/action/end/endoresd/review/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_end_year_endorsed_emp(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_end_year_endorsed_emp()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
    
    
    @http.route(['/action/end/endoresd/hod/<int:confirm_id>'], type='http', auth="public", website=True)
    def action_end_year_endorse_hod(self,confirm_id , access_token=None, **kw):
        id=confirm_id
        record = request.env['hr.appraisal.feedback'].sudo().browse(id)

        record.action_end_year_endorse_hod()
        try:
            approval_sudo = self._document_check_access('hr.appraisal.feedback', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._feedback_get_page_view_values(approval_sudo, **kw) 
        return request.redirect('/appraisal/feedback/%s'%(record.id))
        
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'objective_count' in counters:
            values['objective_count'] = request.env['hr.appraisal.objective'].search_count([('employee_id.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _appraisal_get_page_view_values(self,appraisal, next_id = 0,pre_id= 0, appraisal_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values = {
            'page_name' : 'appraisal',
            'appraisal' : appraisal,
            'edit_objective': False,
            'appraisal_user_flag': appraisal_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(appraisal, access_token, values, 'my_appraisal_history', False, **kwargs)

    def _appraisal_edit_get_page_view_values(self,appraisal, edit_objective, next_id = 0,pre_id= 0, appraisal_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        
        values = {
            'page_name' : 'appraisal',
            'appraisal' : appraisal,
            'appraisal_user_flag': appraisal_user_flag,
            'next_id' : next_id,
             'edit_objective': edit_objective,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(appraisal, access_token, values, 'my_appraisal_history', False, **kwargs)

    
    @http.route(['/appraisal/objectives', '/appraisal/objective/page/<int:page>'], type='http', auth="user", website=True)
    def portal_appraisal_objectives(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'waiting','confirm'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'waiting': {'label': _('Submitted'), 'domain': [('state', '=', 'waiting')]},  
            'confirmed': {'label': _('Approved'), 'domain': [('state', '=', 'confirm')]},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in No#')},
            'name': {'input': 'name', 'label': _('Search in Name')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')}, 
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        appraisal_groups = request.env['hr.appraisal.objective'].search([])

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
#         domain = []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]       

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('employee_id.name', 'all'):
                search_domain = OR([search_domain, [('employee_id.name', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
        domain += ['|',('employee_id.user_id', '=', http.request.env.context.get('uid')),('employee_id.parent_id.user_id', '=', http.request.env.context.get('uid'))]    
 
        appraisal_count = request.env['hr.appraisal.objective'].search_count(domain)

        pager = portal_pager(
            url="/appraisal/objectives",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=appraisal_count,
            page=page,
            step=self._items_per_page
        )

        _appraisals = request.env['hr.appraisal.objective'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_appraisal_history'] = _appraisals.ids[:100]

        grouped_appraisals = [_appraisals]
                
        paging(0,0,1)

        paging(grouped_appraisals)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_appraisals': grouped_appraisals,
            'page_name': 'appraisal',
            'default_url': '/appraisal/objectives',
            'pager': pager,
            'company_info': company_info,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_appraisal.portal_appraisal_objectives", values)

   
    @http.route(['/appraisal/objective/<int:appraisal_id>'], type='http', auth="user", website=True)
    def portal_appraisal_objective(self, appraisal_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = appraisal_id
        try:
            appraisal_sudo = self._document_check_access('hr.appraisal.objective', appraisal_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        appraisal_user_flag = 0
                
        appraisal_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        appraisal_id_list.sort()
        length_list = len(appraisal_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if appraisal_id in appraisal_id_list:
                appraisal_id_loc = appraisal_id_list.index(appraisal_id)
                if appraisal_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif appraisal_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
            

        values = self._appraisal_get_page_view_values(appraisal_sudo,next_id, pre_id, appraisal_user_flag,access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_objective", values)
    
    
    # Appraisal Edit Objective
    
    @http.route(['/appraisal/edit/objective/<int:appraisal_id>'], type='http', auth="user", website=True)
    def edit_portal_appraisal_objective(self, appraisal_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = appraisal_id
        try:
            appraisal_sudo = self._document_check_access('hr.appraisal.objective', appraisal_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        appraisal_user_flag = 0
                
        appraisal_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        appraisal_id_list.sort()
        length_list = len(appraisal_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if appraisal_id in appraisal_id_list:
                appraisal_id_loc = appraisal_id_list.index(appraisal_id)
                if appraisal_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif appraisal_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
            
        edit_objective = True
        values = self._appraisal_edit_get_page_view_values(appraisal_sudo, edit_objective,next_id, pre_id, appraisal_user_flag,access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_objective", values)

    

    @http.route(['/appraisal/next/<int:appraisal_id>'], type='http', auth="user", website=True)
    def portal_appraisal_next(self, appraisal_id, access_token=None, **kw):
        
        appraisal_id_list = paging(0,1,0)
        next_next_id = 0
        appraisal_id_list.sort()
        
        length_list = len(appraisal_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        
        if appraisal_id in appraisal_id_list:
            appraisal_id_loc = appraisal_id_list.index(appraisal_id)
            next_next_id = appraisal_id_list[appraisal_id_loc + 1] 
            next_next_id_loc = appraisal_id_list.index(next_next_id)
            if next_next_id_loc == length_list:
                next_id = 0
                pre_id = 1
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in appraisal_id_list:
                if ids < appraisal_id:
                    buffer_smaller = ids
                if ids > appraisal_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                
            next_next_id_loc = appraisal_id_list.index(next_next_id)
            length_list = len(appraisal_id_list)
            length_list = length_list + 1
            if next_next_id_loc == length_list:
                next_id = 0
                pre_id = 1
            elif next_next_id_loc == 0:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1
         
        values = []
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = appraisal_id
        try:
            appraisal_sudo = self._document_check_access('hr.appraisal.objective', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        appraisal_user_flag = 0


        values = self._appraisal_get_page_view_values(appraisal_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_objective", values)

  
    @http.route(['/appraisal/pre/<int:appraisal_id>'], type='http', auth="user", website=True)
    def portal_appraisal_previous(self, appraisal_id, access_token=None, **kw):
        
        appraisal_id_list = paging(0,1,0)
        pre_pre_id = 0
        appraisal_id_list.sort()
        length_list = len(appraisal_id_list)
    
        if length_list == 0:
            return request.redirect('/my')
        
        length_list = length_list - 1
        if appraisal_id in appraisal_id_list:
            appraisal_id_loc = appraisal_id_list.index(appraisal_id)
            pre_pre_id = appraisal_id_list[appraisal_id_loc - 1] 
            pre_pre_id_loc = appraisal_id_list.index(appraisal_id)

            if appraisal_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in appraisal_id_list:
                if ids < appraisal_id:
                    buffer_smaller = ids
                if ids > appraisal_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = appraisal_id_list.index(pre_pre_id)
            length_list = len(appraisal_id_list)
            length_list = length_list -1
            if pre_pre_id_loc == 0:
                next_id = 1
                pre_id = 0
            elif pre_pre_id_loc == length_list:
                next_id = 0
                pre_id = 1
            else:
                next_id = 1
                pre_id = 1
   
        values = []
        active_user = http.request.env.context.get('uid')
        appraisal_user = []
        id = pre_pre_id
        try:
            appraisal_sudo = self._document_check_access('hr.appraisal.objective', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        appraisal_user_flag = 0
        
        values = self._appraisal_get_page_view_values(appraisal_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_objective", values)
    
################################################################
#         Appraisal FeedBack
################################################################
    
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'feedback_count' in counters:
            values['feedback_count'] = request.env['hr.appraisal.feedback'].search_count([('name.user_id', '=', http.request.env.context.get('uid') )])
        return values
  
    def _feedback_get_page_view_values(self,feedback, next_id = 0,pre_id= 0, feedback_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        manager_edit = False
        edit_flag =  False
        review_flag = False
        values = {
            'page_name' : 'feedback',
            'feedback' : feedback,
            'review_flag': review_flag,
            'manager_edit': manager_edit,
            'edit_flag': edit_flag,
            'full_review_flag': False,
            'full_manager_edit':False,
            'full_edit_flag': False,
            'feedback_user_flag': feedback_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(feedback, access_token, values, 'my_feedback_history', False, **kwargs)
    
    
    def _edit_feedback_get_page_view_values(self,feedback, full_edit_flag, full_review_flag, full_manager_edit, manager_edit, edit_flag, review_flag, next_id = 0,pre_id= 0, feedback_user_flag = 0, access_token = None, **kwargs):
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values = {
            'page_name' : 'feedback',
            'feedback' : feedback,
            'review_flag': review_flag,
            'manager_edit': manager_edit,
            'edit_flag': edit_flag,
            'full_review_flag': full_review_flag,
            'full_manager_edit':full_manager_edit,
            'full_edit_flag': full_edit_flag,
            'feedback_user_flag': feedback_user_flag,
            'next_id' : next_id,
            'company_info': company_info,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(feedback, access_token, values, 'my_feedback_history', False, **kwargs)

    @http.route(['/appraisals/feedback', '/appraisals/feedback/page/<int:page>'], type='http', auth="user", website=True)
    def portal_appraisals_feedback(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'expired','confirm','sent','endorsed_employee','endorsed_hod','done','end_year_appraisee_review',
'end_year_appraiser_review','end_year_sent_emp_view','end_year_endorsed_emp','end_yaer_endorse_hod','closed'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'waiting': {'label': _('Expire'), 'domain': [('state', '=', 'expired')]},  
            'confirmed': {'label': _('Approved'), 'domain': [('state', '=', 'confirmed')]},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in No#')},
            'name': {'input': 'name', 'label': _('Search in Name')},
            'name.name': {'input': 'name.name', 'label': _('Search in Employee')}, 
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        feedback_groups = request.env['hr.appraisal.feedback'].search([])

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
#         domain = []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]       

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('employee_id.name', 'all'):
                search_domain = OR([search_domain, [('name.name', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
        domain += ['|','|',('name.user_id', '=', http.request.env.context.get('uid')),('name.parent_id.user_id', '=', http.request.env.context.get('uid')),('name.department_id.manager_id.user_id', '=', http.request.env.context.get('uid'))]     
        feedback_count = request.env['hr.appraisal.feedback'].search_count(domain)

        pager = portal_pager(
            url="/appraisals/feedback",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=feedback_count,
            page=page,
            step=self._items_per_page
        )

        _feedbacks = request.env['hr.appraisal.feedback'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_feedback_history'] = _feedbacks.ids[:100]

        grouped_feedbacks = [_feedbacks]
                
        paging(0,0,1)

        paging(grouped_feedbacks)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_feedbacks': grouped_feedbacks,
            'page_name': 'feedback',
            'default_url': '/appraisals/feedback',
            'pager': pager,
            'company_info': company_info,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_appraisal.portal_appraisal_feedbacks", values)
    
    
    @http.route(['/edit/appraisal/feedback/<int:feedback_id>'], type='http', auth="user", website=True)
    def edit_portal_appraisal_feedback(self, feedback_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        feedback_user = []
        id = feedback_id
        try:
            feedback_sudo = self._document_check_access('hr.appraisal.feedback', feedback_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        feedback_user_flag = 0
                
        feedback_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        feedback_id_list.sort()
        length_list = len(feedback_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if feedback_id in feedback_id_list:
                feedback_id_loc = feedback_id_list.index(feedback_id)
                if feedback_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif feedback_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
            
        edit_flag = False
        review_flag = False
        manager_edit = False
        if feedback_sudo.state == 'draft':           
            edit_flag = True
        if feedback_sudo.state == 'sent' and feedback_sudo.name.parent_id.user_id.id == http.request.env.context.get('uid'):                         manager_edit = True              
        if feedback_sudo.state == 'sent' and feedback_sudo.name.user_id.id == http.request.env.context.get('uid'):    
           review_flag = True 
        if feedback_sudo.state == 'end_year_sent_emp_view' and feedback_sudo.name.user_id.id == http.request.env.context.get('uid'):   
           review_flag = True   
        if feedback_sudo.state == 'confirm':              
            manager_edit = True 
        full_edit_flag = False
        full_review_flag = False
        full_manager_edit = False
        if feedback_sudo.state == 'end_year_appraisee_review' and feedback_sudo.name.user_id.id == http.request.env.context.get('uid'):           
            full_edit_flag = True
        if feedback_sudo.state == 'end_year_sent_emp_view' and feedback_sudo.name.user_id.id == http.request.env.context.get('uid'):              
            full_review_flag = True
        if feedback_sudo.state == 'end_year_appraiser_review'and feedback_sudo.name.parent_id.user_id.id == http.request.env.context.get('uid'):              
            full_manager_edit = True
        if feedback_sudo.state == 'end_year_sent_emp_view'and feedback_sudo.name.parent_id.user_id.id == http.request.env.context.get('uid'):              
            full_manager_edit = True    
        values = self._edit_feedback_get_page_view_values(feedback_sudo, full_edit_flag, full_review_flag, full_manager_edit, manager_edit, edit_flag, review_flag, next_id, pre_id, feedback_user_flag,access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_feedback", values)

   
    @http.route(['/appraisal/feedback/<int:feedback_id>'], type='http', auth="user", website=True)
    def portal_appraisal_feedback(self, feedback_id, access_token=None, **kw):
        values = []
        active_user = http.request.env.context.get('uid')
        feedback_user = []
        id = feedback_id
        try:
            feedback_sudo = self._document_check_access('hr.appraisal.feedback', feedback_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')        

        feedback_user_flag = 0
                
        feedback_id_list = paging(0,1,0)
        next_id = 0
        pre_id = 0
        next_next_id = 0
        feedback_id_list.sort()
        length_list = len(feedback_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if feedback_id in feedback_id_list:
                feedback_id_loc = feedback_id_list.index(feedback_id)
                if feedback_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif feedback_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0
            
        
        values = self._feedback_get_page_view_values(feedback_sudo, next_id, pre_id, feedback_user_flag,access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_feedback", values)

    @http.route(['/feedback/next/<int:feedback_id>'], type='http', auth="user", website=True)
    def portal_feedback_next(self, feedback_id, access_token=None, **kw):
        
        feedback_id_list = paging(0,1,0)
        next_next_id = 0
        feedback_id_list.sort()
        
        length_list = len(feedback_id_list)
        if length_list == 0:
            return request.redirect('/my')
        length_list = length_list - 1
        
        if feedback_id in feedback_id_list:
            feedback_id_loc = feedback_id_list.index(feedback_id)
            next_next_id = feedback_id_list[feedback_id_loc + 1] 
            next_next_id_loc = feedback_id_list.index(next_next_id)
            if next_next_id_loc == length_list:
                next_id = 0
                pre_id = 1
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in feedback_id_list:
                if ids < feedback_id:
                    buffer_smaller = ids
                if ids > feedback_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                
            next_next_id_loc = feedback_id_list.index(next_next_id)
            length_list = len(feedback_id_list)
            length_list = length_list + 1
            if next_next_id_loc == length_list:
                next_id = 0
                pre_id = 1
            elif next_next_id_loc == 0:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1
         
        values = []
        active_user = http.request.env.context.get('uid')
        feedback_user = []
        id = feedback_id
        try:
            feedback_sudo = self._document_check_access('hr.appraisal.feedback', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        feedback_user_flag = 0


        values = self._feedback_get_page_view_values(feedback_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_feedback", values)

  
    @http.route(['/feedback/pre/<int:feedback_id>'], type='http', auth="user", website=True)
    def portal_feedback_previous(self, feedback_id, access_token=None, **kw):
        
        feedback_id_list = paging(0,1,0)
        pre_pre_id = 0
        feedback_id_list.sort()
        length_list = len(feedback_id_list)
    
        if length_list == 0:
            return request.redirect('/my')
        
        length_list = length_list - 1
        if feedback_id in feedback_id_list:
            feedback_id_loc = feedback_id_list.index(feedback_id)
            pre_pre_id = feedback_id_list[feedback_id_loc - 1] 
            pre_pre_id_loc = feedback_id_list.index(feedback_id)

            if feedback_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in feedback_id_list:
                if ids < feedback_id:
                    buffer_smaller = ids
                if ids > feedback_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = feedback_id_list.index(pre_pre_id)
            length_list = len(feedback_id_list)
            length_list = length_list -1
            if pre_pre_id_loc == 0:
                next_id = 1
                pre_id = 0
            elif pre_pre_id_loc == length_list:
                next_id = 0
                pre_id = 1
            else:
                next_id = 1
                pre_id = 1
   
        values = []
        active_user = http.request.env.context.get('uid')
        feedback_user = []
        id = pre_pre_id
        try:
            feedback_sudo = self._document_check_access('hr.appraisal.feedback', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        feedback_user_flag = 0
        
        values = self._feedback_get_page_view_values(feedback_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_portal_appraisal.portal_appraisal_feedback", values)

