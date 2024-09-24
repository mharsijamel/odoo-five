from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    steg_credit = fields.Float('STEG Credit', tracking=True, store=True, default=0.0)
    sub_anme = fields.Float('ANME Subvention', tracking=True, store=True, default=0.0)

    net_to_pay = fields.Float('Net to pay', digits=(16, 3), store=True, tracking=True, compute='get_net_to_pay')

    @api.onchange('sub_anme', 'steg_credit', 'amount_total')
    @api.depends('sub_anme', 'steg_credit', 'amount_total')
    def get_net_to_pay(self):
        for order in self:
            net_to_pay = order.amount_total
            if order.sub_anme and order.steg_credit:
                net_to_pay = order.amount_total - order.sub_anme - order.steg_credit
            elif order.sub_anme and not order.steg_credit:
                net_to_pay = order.amount_total - order.sub_anme
            elif not order.sub_anme and order.steg_credit:
                net_to_pay = order.amount_total - order.steg_credit
            else:
                net_to_pay = order.amount_total
            order.net_to_pay = net_to_pay
