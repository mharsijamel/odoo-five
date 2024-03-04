# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# Part of AktivSoftware License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# for licensing details.

# Author: Aktiv Software.
# mail:   odoo@aktivsoftware.com
# Copyright (C) 2015-Present Aktiv Software PVT. LTD.
# Contributions:
#           Aktiv Software:
#              - Mital Parmar
#              - Yagnesh Board
#              - Tanvi Gajera
#              - Saurabh Yadav

{
    'name': "Customer Sale History",
    "author": "Aktiv",
    "website": "http://www.aktivsoftware.com",
    'summary': """
        User can view the products which the customer have
        purchased just in a View easily.With the help of
        this module you can learn more about your Customers
        and their shopping habits.
        """,

    'description': """
        Title: Customer Sale History \n
        Author: Aktiv Software \n
        mail: odoo@aktivsoftware.com \n
        Copyright (C) 2015-Present Aktiv Software PVT. LTD.
    """,

    'license': "AGPL-3",
    "contributors": "Aktiv Software",
    'category': 'Sales',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale_management'
    ],

    # always loaded
    'data': [
        'views/res_partner_views.xml',
    ],
    'images': [
        'static/description/banner.jpg',
    ],

    "installable": True,
    "application": True,
    "auto_install": False
}
