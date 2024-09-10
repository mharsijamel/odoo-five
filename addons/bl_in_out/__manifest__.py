# -*- coding: utf-8 -*-
{
    'name': "BL IN/OUT",

    'summary': """add to stock BL in / OUT link to menu
       """,
    'description': """
      add to stock BL in / OUT link to menu
    """,
    'author': "jamel mharsi",
    'website': "http://webvue.tn",
    'category': 'account',
    'depends': ['base','stock','sale','purchase'],
    'version': '1.0.0',
    'data': [
        'views/StockPicking.xml',
    ],
    'installable': True,
    'auto_install': False,
}
