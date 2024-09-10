# -*- coding: utf-8 -*-
{
    'name': "fleet custom",

    'summary': """add car id in employee
       """,
    'description': """
       add car id in employee
    """,
    'author': "jamel mharsi",
    'website': "http://webvue.tn",
    'category': 'fleet',
    'depends': ['base','fleet','account'],
    'version': '1.0.0',
    'data': [
        'views/HREmployee.xml',
        'views/analytic.xml',
        'views/vehicle.xml',
    ],
    'installable': True,
    'auto_install': False,
}
