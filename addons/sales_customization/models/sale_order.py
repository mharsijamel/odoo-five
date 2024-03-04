from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    net_to_pay = fields.Float('Net to pay', digits=(16, 3), store=True, tracking=True, compute='get_net_to_pay')

    @api.onchange('sub_anme', 'steg_credit', 'amount_total')
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


    @api.depends('amount_total', 'net_to_pay')
    def get_amount_letter(self):
        if self.amount_total != self.net_to_pay:
            amount = self.currency_id.amount_to_text(self.net_to_pay)
        else:
            amount = self.currency_id.amount_to_text(self.amount_total)
        return amount



