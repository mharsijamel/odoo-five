{
    'name': 'Technical Team Folder For sale Order',
    'version': '15.0.0.1',
    'summary': 'Technical Team Folder For sale Order',
    'description': 'Technical Team Folder For sale Order',
    'category': 'Sales',
    'author': 'Infotech Consulting Services (ICS)',
    'website': 'http://ics-tunisie.com',
    'license': 'LGPL-3',
    'depends': ['sale', 'project', 'stock', 'custom_crm_lead', 'sales_team'],
    'data': [
            'security/security_groups.xml',
            'security/ir.model.access.csv',
            'views/technical_team_views.xml',
            'views/technical_folder_views.xml',
            'views/sale_order_views.xml',
            # 'views/',
            # 'views/',
    ],
    'installable': True,
    'auto_install': False
}
