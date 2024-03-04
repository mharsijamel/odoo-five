# -*- coding: utf-8 -*-
{
    'name': "Document Treasury Menu",
    'summary': """
        Document Treasury Menu""",

    'description': """
        Document Treasury Menu 
    """,

    'author': "Infotech Consulting Services (ICS)",
    'website': "https://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base','l10n_tn_treasury'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/treasury_groups.xml',
        'views/menu.xml',
    ],
}
