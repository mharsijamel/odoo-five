# Copyright Netformica - Mohamed Machta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': "Tunisia Stamp Tax",
    'version': '14.0.0.2',
    'author': "Montassar Ben Abdelkader, ICS Tunisie",
    'website': "http://www.ics-tunisie.com",
    'category': 'Localisation',
    "license": "LGPL-3",
    'depends': ['base', 'account', 'l10n_tn', 'sale'],
    'application': False,
    'data': [
        'views/fiscal_position.xml',
        'data/fiscal_position.xml',
        'views/invoice.xml',
        'views/account_tax_view.xml',
        'views/report_invoicel.xml',
        'views/report_quote.xml',
    ],
    'images': [
        'static/description/screen.jpg',
    ],
    "pre_init_hook":  "pre_init_check",
}
