# -*- coding: utf-8 -*-
{
    'name': "complaint_to_supplier",

    'summary': """
        Complaint to Supplier""",
    'description': """
        Complaint to Supplier
    """,
    'author': "Infotech Consulting Services (ICS)",
    'website': "http://www.ics-tn.com",
    'category': 'Uncategorized',
    'version': '13.0.0.2',
    'depends': ['base', 'purchase','custom_purchase_order','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/purchase_complaint_view.xml',
        'views/res_partner_view_ih.xml',
        'views/purchase_order_view_ih.xml',
        'data/complaint_to_supplier_sequence.xml',
        'data/complaint_to_supplier_mail_template.xml',
        'data/mail_data.xml',
    ],
}
