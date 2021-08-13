# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "HR Employee Profile Report",
    "category": 'HR',
    "summary": "Generate HR Employee Profile Report",
    "description": """Generate HR Employee Profile Report
    """,
    "sequence": 1,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    "version": '14.1.0.0',
    "depends": ['base', 'hr', 'account'],
    # "depends": ['base', 'hr', 'report_xlsx', 'de_employee_overtime'],
    "data": [
        #'security/ir.model.access.csv',
        'reports/employee_profile.xml',
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
