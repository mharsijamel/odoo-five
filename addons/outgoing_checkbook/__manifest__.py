# -*- coding: utf-8 -*-
{
    'name': "Checkbook Manager",

    'summary': """
        Checkbook Manager""",

    'description': """
        Checkbook Manager
    """,
    'author': "Infotech Consulting Services (ICS)",
    'website': "http://www.ics-tn.com/",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['web','base','account',],
    'data': [
        'wizard/account_checkbook_wizard_view.xml',
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/bank_names.xml',
        'views/checkbook_views.xml',
        'views/cheque_views.xml',
        'views/menu.xml',
        'views/payment_view_inhiret.xml',
        'views/account_payment_register_form_inherit.xml',
        'views/account_journal_views.xml',
    ],
}
