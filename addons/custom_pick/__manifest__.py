# -*- coding: utf-8 -*-
{
    'name': "Custom pick",

    'summary': """add ale price to delivery
       """,
    'description': """
       add ale price to delivery
    """,
    'author': "jamel mharsi",
    'website': "http://webvue.tn",
    'category': 'account',
    'depends': ['base','stock'],
    'version': '1.0.0',
    'data': [
        'views/sale_price.xml',
        'report/sale_delivery_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
