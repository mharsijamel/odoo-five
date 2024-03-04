# -*- coding: utf-8 -*-
{
    'name': "Tunisia - Accounting",
    'description': """
        This module implements the accounting chart for Tunisia area.
    """,
    'author': "Infotech Consulting Services Tunisie",
    'website': "http://www.ics-tunisie.com",
    "category": 'Accounting/Localizations/Account Charts',
    'version': '15.0.0.1',
    'license': 'AGPL-3',
    "depends": ['base', 'account'],
    'data': [
        'data/account_tax.xml',
        'data/l10n_tn_chart_data.xml',
        'data/account.account.template.csv',
        'data/account_tax_template_data.xml',
        'data/l10n_tn_chart_post_data.xml',
    ],
    'images': ['images/plan_comptable.png'],
    'price': 49.99,
    'currency': 'EUR',
    "pre_init_hook":  "pre_init_check",


}
