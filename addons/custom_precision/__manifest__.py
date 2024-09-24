# -*- coding: utf-8 -*-
{
    'name': "Custom Precision",
    'summary': """
        Custom Precision""",

    'description': """
        Custom Precision
    """,
    'author': "Infotech Consulting Services",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1.0',
    'depends': ['base', 'account', 'sale', 'purchase'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/invoice_report_inherit.xml',
        'views/purchase_order_report_inherit.xml',
        'views/sale_order_report_inherit.xml',
    ],
}
