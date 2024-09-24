# -*- coding: utf-8 -*-
{
    'name': "Customer Reference Search",
    'summary': """
        Customer Reference Search""",
    'description': """
        Customer Reference Search
    """,
    'author': "Infotech Consulting Services",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base','crm','custom_crm_lead'],
    'data': [
        # 'security/ir.model.access.csv'
        'views/customer_reference_view.xml',
        'views/menu.xml',

    ],
}
