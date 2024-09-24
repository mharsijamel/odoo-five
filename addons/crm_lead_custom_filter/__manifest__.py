# -*- coding: utf-8 -*-
{
    'name': "Crm Lead Custom Filter",
    'summary': """
        Crm lead Custom Filter""",
    'description': """
        Crm lead Custom Filter
    """,
    'author': "Infotech Consulting Services",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1.0',
    'depends': ['base', 'crm','pumping_project','sale','custom_sale_order','stock','account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/crm_lead_custom.xml',
        'views/sale_order_custom_view.xml',
        'views/account_move_view_inherit.xml',
        'views/stock_picking_view.xml'
    ],
}
