# -*- coding: utf-8 -*-
{
    'name': "Project Consumption Information",
    'summary': """
        Project Consumption Information""",
    'description': """
        Project Consumption Information
    """,
    'author': "Infotech Consulting Services (ICS)",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base','project','stock','sale',],
    'data': [
        'security/ir.model.access.csv',
        'views/project_project_view_inherit.xml',
    ],
}
