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
    
    
    @http.route('/appraisal/objective/save', type="http", auth="public", website=True)
    def edit_objective(self, **kw):
        global appraisal_objective_list
        objective_val = {
            'description': kw.get('description'),
            'employee_id': int(kw.get('employee_id')),
            'objective_year': kw.get('objective_year'),
        }
        record = request.env['hr.appraisal.objective'].sudo().create(objective_val)
        for worker in appraisal_objective_list:
            line_vals = {
                'objective_id': record.id,
                'objective':  worker['objective'],
                'weightage':  worker['weightage'],
                'priority': worker['priority'],
                }
            record_lines = request.env['hr.appraisal.objective.line'].sudo().create(line_vals)
        appraisal_objective_list = []
        return request.render("de_portal_appraisal.appraisal_submited", {})
    
    
    
    @http.route('/appraisal/create/',type="http", website=True, auth='user')
    def appraisal_template(self, **kw):
        global appraisal_objective_list
        appraisal_objective_list = []
        return request.render("de_portal_appraisal.portal_appraisal",appraisal_page_content()) 
    
 
    
    @http.route('/appraisal/objective/save', type="http", auth="public", website=True)
    def create_appraisal_objective(self, **kw):
        global appraisal_objective_list
        objective_val = {
            'description': kw.get('description'),
            'employee_id': int(kw.get('employee_id')),
            'objective_year': kw.get('objective_year'),
        }
        record = request.env['hr.appraisal.objective'].sudo().create(objective_val)
        for worker in appraisal_objective_list:
            line_vals = {
                'objective_id': record.id,
                'objective':  worker['objective'],
                'weightage':  worker['weightage'],
                'priority': worker['priority'],
                }
            record_lines = request.env['hr.appraisal.objective.line'].sudo().create(line_vals)
        appraisal_objective_list = []
        return request.render("de_portal_appraisal.appraisal_submited", {})
    
    
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
            'appraisal_user_flag': appraisal_user_flag,
            'next_id' : next_id,
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
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'waiting','confirmed'])]},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'waiting': {'label': _('Submitted'), 'domain': [('state', '=', 'waiting')]},  
            'confirmed': {'label': _('Approved'), 'domain': [('state', '=', 'confirmed')]},
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
        values = {
            'page_name' : 'feedback',
            'feedback' : feedback,
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
            'all': {'label': _('All'), 'domain': [('state', 'in', ['draft', 'expired','confirmed','sent','endorsed_employee','endorsed_hod','done','end_year_appraisee_review',
'end_year_appraiser_review','end_year_sent_emp_review','end_year_endorsed_emp','end_yaer_endorse_hod','closed'])]},
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
                feedback_id_loc = feedbackl_id_list.index(feedback_id)
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
            

        values = self._feedback_get_page_view_values(feedback_sudo,next_id, pre_id, feedback_user_flag,access_token, **kw) 
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
        return request.render("de_portal_appraisal.portal_appraisal_objective", values)

  
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
        return request.render("de_portal_appraisal.portal_appraisal_objective", values)

