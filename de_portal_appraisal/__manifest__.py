# -*- coding: utf-8 -*-
{
    'name': "Portal Appraisal",

    'summary': """
        Portal Appraisal Objective
        """,

    'description': """
        Portal Appraisal Objective
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Appraisal',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web', 'hr_appraisal','de_hr_portal_user','de_expense_enhancement'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_appraisal_objective_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
