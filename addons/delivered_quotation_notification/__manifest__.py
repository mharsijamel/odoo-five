# -*- coding: utf-8 -*-
{
    'name': "Delivered Quotation Notification",
    'summary': """ Delivered Quotation Notification""",

    'description': """
        Delivered Quotation Notification
    """,
    'author': "Infotech Consulting Services",
    'website': "http://www.ics-tn.com",

    'category': 'Uncategorized',
    'version': '15.0.0.1.0',
    'depends': ['base','stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/delivred_quotation_notification.xml',
        'data/delivred_notification.xml',
    ],
}
