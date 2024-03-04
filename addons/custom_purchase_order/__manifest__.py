{
    'name': 'Custom Purchase Order Fields',
    'version': '13.0.0.1',
    'summary': 'Custom Purchase Order and partner Fields',
    'description': 'Custom Purchase Order and partner Fields',
    'category': 'Purchase',
    'author': 'Odeon Business Solution (ODBS)',
    'website': 'https://ics-tn.com',
    'license': 'OPL-1',
    'depends': ['base', 'purchase'],
    'data': [
            'security/l10n_tn_groups.xml',
            'views/res_partner_views.xml',
            'views/purchase_order_views.xml',
            'data/mail_data.xml',
    ],
    'installable': True,
    'auto_install': False
}
