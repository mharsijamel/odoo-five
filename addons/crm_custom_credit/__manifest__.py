# -*- coding: utf-8 -*-
{
    'name': "Crm Custom Credit",
    'summary': """
        Crm Custom Credit""",
    'description': """
        Crm Custom Credit
    """,
    'author': "Infotech Consulting Services(ICS)",
    'website': "https://ics-tunisie.com/",
    'category': 'Sales',
    'version': '15.0.0.1',
    'license': 'LGPL-3',
    'depends': ['custom_crm_lead', 'pumping_project'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/crm_lead_inherit_view.xml',
    ],
}
