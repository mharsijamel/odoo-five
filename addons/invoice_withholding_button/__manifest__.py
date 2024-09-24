# -*- coding: utf-8 -*-
{
    'name': " Invoice Withholding Button",
    'description': """
        add withholding button in Invoice
    """,
    'author': "Infotech Consulting Services(ICS)",
    'website': "https://www.ics-tn.com",
    'version': '15.0.0.1',
    'depends': ['base', 'account', 'l10n_tn_ras'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/rs_bottom_add_inhview.xml',
        'reports/report_invoice.xml',
    ],

}
