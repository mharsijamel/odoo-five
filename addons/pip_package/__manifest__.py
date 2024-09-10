# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Install pip packages',
    'version': '15.0.1.1.2',
    'category': 'Extra Tools',
    'live_test_url':'https://youtu.be/0kVWD5G59M8',
    'summary': 'You can install any pip module',
    'author': 'Odolution',
    'maintainer': 'Shaikh Huzaifa',
#     'price': 10.00,
#     'currency': "USD",
    'license': 'LGPL-3',
    'depends': [],
    'demo': [],
    'data': [
        'pip_install.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['images/1.PNG', 'images/2.PNG', 'images/3.PNG','images/4.PNG','static/description/icon.png'],
    'installable': True,
    'application': True,
}
