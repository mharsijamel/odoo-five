# -*- coding: utf-8 -*-
{
    'name': "Post Installation",
    'summary': """
        Post Installation""",
    'description': """
        Post Installation
    """,
    'author': "Infotech Consulting Services (ICS)",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base','mail','stock','sale','project','custom_crm_lead','after_sale_service','project_consumption_information'],
    'data': [
        'security/ir.model.access.csv',
        'security/post_installation_groups.xml',

        'views/post_installation_views.xml',
        'views/project_project_view_inherit.xml',
        'views/menu.xml',
        'views/sale_order_inherit_view.xml',
        'data/act_mail.xml',
    ],

}
