# -*- encoding: utf-8 -*-


from odoo import fields, api, models, _


class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.depends('amount_total')
    def get_amount_letter(self):
        amount = self.currency_id.amount_to_text(self.amount_total)
        return amount
