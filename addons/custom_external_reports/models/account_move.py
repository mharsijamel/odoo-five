from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    counter_id = fields.Many2one('customer.reference', string='Counter Reference', domain="[('partner_id', '=', partner_id)]")
    power_level = fields.Float(string='Nb. KWC')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = super(SaleOrder, self)._prepare_invoice_values(order, name, amount, so_line)
        if order.counter_id:
            invoice_vals['counter_id'] = order.counter_id.id
        if order.opportunity_id.power_level:
            invoice_vals['power_level'] = order.opportunity_id.power_level
        return invoice_vals
