# -*- coding: utf-8 -*-
{
    'name': "crm lead win date",
    'summary': """
        CRM Lead Win Date""",
    'description': """
        CRM Lead Win Date
    """,
    'author': "Infotech Consulting Services",
    'website': "http://www.ics-tn.com",
    'category': 'CRM',
    'version': '15.0.0.1.0',
    'depends': ['base', 'crm'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/crm_lead_view.xml',
        'views/res_partner_view.xml',
    ],
}
