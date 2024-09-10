# -*- coding: utf-8 -*-
{
    'name': "SIGNATURE",

    'summary': """ajout SIGNATURE SOCIETE 
       """,
    'description': """
       ajout SIGNATURE SOCIETE 
    """,
    'author': "jamel mharsi",
    'website': "http://webvue.tn",
    'category': 'account',
    'depends': ['base', 'sale'],
    'version': '1.0.0',
    'data': [
        'reports/sale_report_inherit.xml',
        'views/res_company_views.xml',

    ],
    'installable': True,
    'auto_install': False,
}
