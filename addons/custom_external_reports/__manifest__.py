{
    'name': 'Custom External Reports',
    'version': '15.0.0.1.0',
    'summary': 'Custom External Reports',
    'description': 'Custom External Reports',
    'category': 'Extra Tools',
    'author': 'Infotech Consulting Services (ICS)',
    'website': 'https://ics-tunisie.com',
    'license': 'OPL-1',
    'depends': ['base', 'web', 'sale', 'account', 'tax_exemption_certificate', 'custom_crm_lead'],
    'data': [
            'reports/custom_external_reports.xml',
            'reports/custom_invoice_reports.xml',
            'views/account_move_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
