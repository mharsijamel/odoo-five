# -*- coding: utf-8 -*-
{
    'name': "Pumping Project",
    'summary': """
        Pumping Project""",
    'description': """
        Pumping Project
    """,
    'author': "Infotech Consulting Services (ics)",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base','crm','custom_crm_lead','mail','sale', 'technical_team_sale_order'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_inherit_view.xml',
        'views/sale_order_view.xml',
        'views/pumping_config_views.xml',
        'views/menu.xml',
    ],
}
