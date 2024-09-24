# -*- coding: utf-8 -*-
{
    'name': "Confirmed Quotation Notification",
    'summary': """
        Confirmed Quotation Notification""",

    'description': """
        Confirmed Quotation Notification
    """,
    'author': "Infotech Consulting Services",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1.0',
    'depends': ['base','sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/quotattion_notification_groupe.xml',
        'data/sale_notification.xml',
    ],
}
