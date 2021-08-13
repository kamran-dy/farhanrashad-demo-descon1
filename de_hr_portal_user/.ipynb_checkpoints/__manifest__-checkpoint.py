# -*- coding: utf-8 -*-
{
    'name': "Portal User",

    'summary': """
        Portal User On Employee Form
        """,

    'description': """
        Portal User Modification on employee Form.
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','portal','web','approvals'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/approval_request_views.xml',
        'views/hr_employee_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
