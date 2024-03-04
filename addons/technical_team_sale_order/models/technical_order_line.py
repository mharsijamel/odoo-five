# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round


class TechnicalOrderLine(models.Model):
    _name = 'technical.order.line'
    _description = 'Technical Order Line'
    _order = 'order_id, sequence, id'
    _check_company_auto = True

    order_id = fields.Many2one('technical.folder', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Text(string='Description', required=False, default="/")
    sequence = fields.Integer(string='Sequence', default=10)

    product_id = fields.Many2one(
        'product.product', string='Product', domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
    product_template_id = fields.Many2one(
        'product.template', string='Product Template',
        related="product_id.product_tmpl_id", domain=[('sale_ok', '=', True)])
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]", ondelete="restrict")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom_readonly = fields.Boolean(compute='_compute_product_uom_readonly')

    technical_team_id = fields.Many2one(related='order_id.team_id', store=True, string='Technical Team')
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, index=True)
    order_partner_id = fields.Many2one(related='order_id.partner_id', store=True, string='Customer', index=True)
    state = fields.Selection(
        related='order_id.state', string='Order Status', copy=False, store=True)

    @api.depends('state')
    def _compute_product_uom_readonly(self):
        for line in self:
            line.product_uom_readonly = line.ids and line.state in ['done', 'cancel']

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return

        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            self.update({
                'product_uom': self.product_id.uom_id,
                'product_uom_qty': self.product_uom_qty or 1.0
            })


        product = self.product_id
        if product and product.sale_line_warn != 'no-message':
            if product.sale_line_warn == 'block':
                self.product_id = False
            return {
                'warning': {
                    'title': _("Warning for %s", product.name),
                    'message': product.sale_line_warn_msg,
                }
            }
