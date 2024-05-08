# -*- coding: utf-8 -*-
{
    'name': 'TN Checks Layout',
    'version': '1.0',
    'category': 'Accounting/Localizations/Check',
    'summary': 'Print TN Checks',
    'description': """
This module allows to print your payments on pre-printed check paper.
You can configure the output (layout, stubs information, etc.) in company settings, and manage the
checks numbering (if you use pre-printed checks without numbers) in journal settings.

Supported formats
-----------------
This module supports the three most common check formats and will work out of the box with the linked checks from checkdepot.net.


You can choose between:

    """,
    'website': 'https://www.odoo.com/app/accounting',
    'depends' : ['account_check_printing'],
    'data': [
        'data/tn_check_printing.xml',
        'report/print_checks.xml',
        'report/print_check_biatta.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
    'assets': {
       
    }
}
