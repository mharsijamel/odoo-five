# -*- coding: utf-8 -*-
{
    'name': "Print Dynamic treaty",
    'version': "15.0.1.0",
    'summary': "Print Dynamic treaty",
    'description': """Print Dynamic treaty""",
    'category': "Accounting",
    "author": "Infotech Consulting Services (ICS)",
    "website": "http://ics-tn.com",
    "license": "OPL-1",
    "price": 100,
    "currency": 'EUR',
    'depends': ['generate_dynamic_cheque_app'],
    'data': [
        'security/ir.model.access.csv',
        'data/treaty_format_data.xml',
        'reports/dynamic_treaty_report_template.xml',
        'wizard/print_dynamic_treaty_wizard_view.xml',
        'views/dynamic_treaty_view.xml',
    ],
    "images": ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}


