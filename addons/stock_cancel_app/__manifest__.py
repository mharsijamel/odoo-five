# -*- coding: utf-8 -*-

{
    'name': 'Cancel Stock/Cancel Inventory/Cancel Stock Move/Cancel Scrap Order',
    "author": "Edge Technologies",
    'version': '15.0.1.0',
    'live_test_url': "https://youtu.be/p1xTUaXoUR4",
    "images":['static/description/main_screenshot.png'], 
    'summary': 'Cancel Inventory Cancel Stock Picking Cancel Scrap Order Cancel Stock Moves Delete Stock Picking Delete Scrap Order Delete Stock Moves cancel warehouse reverse stock move reverse stock picking reverse stock move cancel scrap order cancel picking reset',
    'description': 'Stock Cancel Odoo App',
    'license': "OPL-1",
    'depends': ['base','stock','sale_management'],
    'data': [
        'security/security.xml',
        'wizard/view_cancel_delivery_wizard.xml',
        'views/res_company.xml',
        'views/res_config_settings.xml',
        'views/stock_move.xml',
        'views/stock_picking.xml',
        'views/stock_picking_action.xml',
        'views/stock_scarp_action.xml',
        'views/stock_scrap.xml',
    ],
    'installable': True,
    'auto_install': False,
    'price': 12,
    'currency': "EUR",
    'category': 'Warehouse',
}