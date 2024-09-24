from odoo import models, fields, api
from itertools import groupby
from odoo.exceptions import AccessError, UserError, ValidationError

class SaleOrder (models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        result.update({
            'steg_credit': self.steg_credit,
            'sub_anme': self.sub_anme,
            })
        return result
