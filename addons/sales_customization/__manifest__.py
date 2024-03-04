{
    'name': 'Sales Customization',
    'version': '15.0.0.1',
    'summary': 'Sales Customization',
    'description': 'Sales Customization',
    'category': 'Sales',
    'author': 'Odeon Business Solution (ODBS)',
    'website': 'https://ics-tn.com',
    'license': 'OPL-1',
    'depends': ['custom_crm_lead', 'l10n_tn_stamp_tax'],
    'data': [
            'views/sale_order_views.xml',
            'views/sale_order_document.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
