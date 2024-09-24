# -*- coding: utf-8 -*-
{
    'name': "Crm Lead Custom Field",
    'summary': """
        Crm Lead Custom Field""",
    'description': """
        Crm Lead Custom Field
    """,
    'author': "Infotech Consulting Services",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base','crm','account','pumping_project','custom_external_reports'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/crm_lead_view.xml',
        'views/account_move_tree_view.xml',
    ],
}
