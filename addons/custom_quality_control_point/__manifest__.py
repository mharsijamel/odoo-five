# -*- coding: utf-8 -*-
{
    'name': "custom_quality_control_point",

    'summary': """
        Custom Quality Alert""",

    'description': """
        Custom Quality Alert
    """,
    'author': "Infotech Consulting Services (ICS)",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '13.0.0.1',
    'depends': ['base','quality_control','stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking_view.xml',
    ],
}
