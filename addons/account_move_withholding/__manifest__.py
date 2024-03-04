# -*- coding: utf-8 -*-
{
    'name': "Account Move withholding",
    'summary': """
        Account Move withholding""",

    'description': """
        Account Move withholding
    """,
    'author': "Infotech Consulting Services (ICS)",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base','account','l10n_tn_ras'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/add_witholding_button.xml',
        'reports/withholding_invoice.xml',
    ],
}
