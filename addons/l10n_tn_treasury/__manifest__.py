# -*- coding: utf-8 -*-
{
    'name': "Document De Trésorerie",
    'summary': """
        Document De Trésorerie""",

    'description': """
        Document De Trésorerie
    """,
    'author': "Infotech Consulting Services(ICS)",
    'website': "https://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base','account','mail', 'outgoing_checkbook', 'account_check_printing'],
    'data': [
        'data/sequence.xml',
        'data/account_treaty_data.xml',
        'security/ir.model.access.csv',
        'views/account_journal_view_inherit.xml',
        'views/account_payment_register_form_inherit.xml',
        'views/account_move_line.xml',
        'views/account_payment_inherit_view.xml',
        'views/menu.xml',
        'views/account_treasury_view.xml',
        'views/account_document_exchange_view.xml',
        'views/account_installment_view.xml',
        'views/account_treasury_installment_view.xml',
        'views/account_installment_trait_view.xml',
        'views/account_withdrawal_cash_view.xml',
        'wizard/document_treasury_unpaid_view.xml',
        'wizard/document_treasury_paid_view.xml',
        'report/vesement_report_views.xml',
        'report/report_traite_vesement.xml',
        'report/report_check_vesement.xml',
        'report/report_cash_vesement.xml',

    ],
}
