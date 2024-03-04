{
    'name': 'Concerned Users For Quotation & Technical Folder Margin',
    'version': '15.0.0.2',
    'summary': 'Concerned Users For Quotation & Technical Folder Margin',
    'description': 'Concerned Users For Quotation & Technical Folder Margin',
    'category': 'Sales',
    'author': 'Infotech Consulting Services (ICS)',
    'website': 'http://ics-tunisie.com',
    'license': 'LGPL-3',
    'depends': ['base', 'sales_team', 'sale','technical_team_sale_order'],
    'data': [
        'security/ir.model.access.csv',
        'data/concerned_users_sequence.xml',
        'views/concerned_users.xml',
    ],
    'installable': True,
    'auto_install': False
}
