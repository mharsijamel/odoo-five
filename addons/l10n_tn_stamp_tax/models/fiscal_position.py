# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class account_fiscal_position(models.Model):

    _inherit = 'account.fiscal.position'

    stamp_tax_id = fields.Many2one(string="Timbre Fiscal Vente", comodel_name="account.tax")
    stamp_tax_id2 = fields.Many2one(string="Timbre Fiscal Achat", comodel_name="account.tax")
