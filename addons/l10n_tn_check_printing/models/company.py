# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Company(models.Model):
    _inherit = "res.company"

    # here, key has to be full xmlID(including the module name) of all the
    # new report actions that you have defined for check layout
    account_check_printing_layout = fields.Selection(selection_add=[
        ('l10n_tn_check_printing.action_print_check_biatta', 'Print Check (biatta) - TN'),
    ], ondelete={
        'l10n_tn_check_printing.action_print_check_biatta': 'set default',
    })
