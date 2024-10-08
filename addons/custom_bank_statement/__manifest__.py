# -*- coding: utf-8 -*-
{
    'name': "Custom Bank Statement",

    'summary': """Custom Bank Statement
       """,
    'description': """
        Custom module to ensure all lines of the bank statement are posted.
    """,
    'author': "jamel mharsi",
    'website': "http://webvue.tn",
    'category': 'accounting',
    'depends': ['base', 'account','account_reports'],
    'version': '1.0.0',
    'data': [
        'views/account_journal_dashboard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
