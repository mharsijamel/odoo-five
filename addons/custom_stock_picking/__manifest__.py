# -*- coding: utf-8 -*-
{
    'name': "Custom Stock Picking",
    'summary': """
        Custom Stock Picking""",
    'description': """
        Custom Stock Picking
    """,
    'author': "Infotech Consulting Services(ICS)",
    'website': "https://website.ics-tn.com/",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base', 'stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking_view.xml',
        'views/stock_picking_report.xml',
    ],
}
