# -*- coding: utf-8 -*-
{
    'name': "anita_form_callback",

    'summary': """extend to support callback for form""",

    'description': """
        extend to support callback for form, so yu can get the result of wizard form from js side, 
        this demo project demonstrates this feature,  this is useful when yu develop client action
    """,

    'author': "funenc odoo team",
    'website': "https://odoo.openerpnext.com",
    'live_test_url': 'https://www.openerpnext.com/@/anita-from-callback',

    'category': 'application',
    'version': '15.0.0.3',
    'price': 0,

    'license': 'OPL-1',
    'images': ['static/description/banner.png'],

    'depends': ['base'],

    "application": False,
    "installable": True,
    "auto_install": False,

    'depends': ['base'],

    'data': [],

    'assets': {
        'web.assets_backend': [
            'anita_form_callback/static/js/anita_form_extend.js'
        ],
        
        'web.assets_qweb': []
    }
}
