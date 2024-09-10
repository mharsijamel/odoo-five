# -*- coding: utf-8 -*-
{
    'name': "Uninvoiced Stock Picking",

    'summary': """ajout champ true or false in res_partner tree view
       """,
    'description': """
       ajout champ true or false in res_partner tree view
    """,
    'author': "jamel mharsi",
    'website': "http://webvue.tn",
    'category': 'account',
    'depends': ['base','stock','sale','account'],
    'version': '1.0.0',
    'data': [
        'views/res_partner.xml',

    ],
    'installable': True,
    'auto_install': False,
}
