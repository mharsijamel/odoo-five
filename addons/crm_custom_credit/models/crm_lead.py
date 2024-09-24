from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    with_credit = fields.Boolean(string='With Credit')

    cash = fields.Boolean(string='Cash')

    @api.onchange('with_credit')
    def _onchange_with_credit(self):
        for rec in self:
            if rec.with_credit:
                rec.sudo().update({
                    'cash': False,
                })

    @api.onchange('cash')
    def _onchange_cash(self):
        for rec in self:
            if rec.cash:
                rec.sudo().update({
                    'with_credit': False,
                })


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    with_credit = fields.Boolean(string='With Credit', related="opportunity_id.with_credit")

    cash = fields.Boolean(string='Cash', related="opportunity_id.cash")
