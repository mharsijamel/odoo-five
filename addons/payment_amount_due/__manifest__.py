{
    'name': 'Payment Amount Due',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Add PAYMENT AMOUNT DUE TO PAYMENTS et total des commandes non facturés',
    'depends': ['account'],
    'data': [
        'views/account_payment_view.xml',
    ],
    'installable': True,
    'application': False,
}
