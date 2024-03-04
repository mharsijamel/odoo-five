# -*- coding: utf-8 -*-
{
    'name': "After Sale Service",
    'summary': """after sale service management""",
    'description': """
        after sale service management
    """,
    'author': "Infotech Consulting Services (ICS)",
    'website': "https://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base','mail',],
    'data': [
        'security/ir.model.access.csv',
        'security/after_sale_groups.xml',
        'views/after_sale_service_views.xml',
        'views/menu.xml',
    ],
}
