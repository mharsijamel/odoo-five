{
    'name': 'Concatenated References in Invoices and Payments',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Adds concatenated payment and invoice references to lists',
    'depends': ['account','l10n_tn_treasury','base'],  # Odoo's Accounting module
    'data': [
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'application': False,
}
