# -*- coding: utf-8 -*-
{
    'name': "Print Dynamic Cheque",
    'version': "15.0.1.0",
    'summary': "Print Dynamic Cheque",
    'description': """Print Dynamic Cheque""",
    'category': "Accounting",
    "author": "Infotech Consulting Services (ICS)",
    "website": "http://ics-tn.com",
    "license": "OPL-1",
    "price": 100,
    "currency": 'EUR',
    'depends': ['base', 'account', 'account_check_printing', 'l10n_tn_treasury'],
    'data': [
        'security/ir.model.access.csv',
        'data/cheque_format_data.xml',
        'reports/dynamic_cheque_report_template.xml',
        'wizard/print_dynamic_cheque_wizard_view.xml',
        'views/dynamic_cheque_view.xml',
    ],
    "images": ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}


