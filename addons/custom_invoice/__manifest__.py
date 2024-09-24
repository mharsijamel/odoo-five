# -*- coding: utf-8 -*-
{
    'name': "Custom Invoice",
    'summary': """
    Custom Invoice
    """,
    'description': """
        Custom Invoice
    """,
    'author': "Infotech Consulting Services(ics)",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base','sale','account','sale_management'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_view.xml',
    ],
}
