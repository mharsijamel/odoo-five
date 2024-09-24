{
    'name': 'Custom Crm Lead',
    'version': '15.0.0.1',
    'summary': 'Custom Crm Lead',
    'description': 'Custom Crm Lead',
    'category': 'CRM',
    'author': 'Infotech Consulting Sevices (ICS)',
    'website': 'http://ics-tn.com',
    'license': 'OPL-1',
    'depends': ['crm', 'sale_crm', 'sale'],
    'data': [
            'security/ir.model.access.csv',
            'data/mail_data.xml',
            'wizards/crm_lead_to_opportunity_views.xml',
            'views/res_partner_views.xml',
            'views/crm_lead_views.xml',
            'views/sale_order_views.xml',

    ],
    'installable': True,
    'auto_install': False
}
