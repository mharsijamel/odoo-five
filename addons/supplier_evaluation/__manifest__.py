# -*- coding: utf-8 -*-
{
    'name': "supplier_evaluation",

    'summary': """
        Supplier Evaluation Module""",

    'description': """
        Supplier Evaluation 
    """,
    'author': "Infotech Consulting Services (ICS)",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '13.0.0.1',
    'depends': ['base','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/supplier_evaluation_view.xml',
        'views/res_partner_view.xml',
        'data/supplier_evaluation.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'supplier_evaluation/static/src/xml/*.xml',
        ],
        'web.assets_backend': [
            'supplier_evaluation/static/src/js/supplier_evaluation.js',
            'supplier_evaluation/static/src/scss/custom_scss.scss',
        ],

    },

}

