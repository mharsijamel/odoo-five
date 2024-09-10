from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)]}, default=fields.Date.today(),)
