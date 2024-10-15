# -*- coding: utf-8 -*-
{
    'name': "Product Cost",

    'summary': """add product cost to invoice
       """,
    'description': """
       add product cost to invoice
    """,
    'author': "jamel mharsi",
    'website': "http://webvue.tn",
    'category': 'account',
    'depends': ['base','account'],
    'version': '1.0.0',
    'data': [
        'views/account_move_line.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'product_cost/static/src/js/preview_cost_product.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}
