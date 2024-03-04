# -*- coding: utf-8 -*-
{
    'name': "Retenue à la Source Tunisien Pour Odoo 14.0",
    'summary': """
        l10n_tn - Retenue à la Source Tunisien Pour Odoo 14.0""",
    'description': """
        l10n_tn - Retenue à la Source Tunisien Pour Odoo 14.0
    """,
    'category': 'Accounting',
    'version': '14.0.1.0',
    'author': "Infotech Consulting Services Tunisie",
    'website': "http://www.ics-tunisie.com",
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_withholding_sequence.xml',
        'views/l10n_tn_withholding_tax_views.xml',
        'views/withholding_tax_view.xml',
        'views/journal_custom_form.xml',
        'views/account_move_view.xml',
        'reports/report_invoice.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "pre_init_hook":  "pre_init_check",
}
