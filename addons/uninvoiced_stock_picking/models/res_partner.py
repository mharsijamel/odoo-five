from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_uninvoiced_stock_picking = fields.Boolean(
        string='BL non Facturé',
        compute='_compute_has_uninvoiced_stock_picking',
        store=True
    )

    @api.depends('sale_order_ids')
    def _compute_has_uninvoiced_stock_picking(self):
        for partner in self:
            # Search for sale orders that do not have any invoices linked
            sale_orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),
                ('invoice_ids', '=', False)
            ])

            uninvoiced = False
            for order in sale_orders:
                # Check if there are related stock pickings that are done
                pickings = self.env['stock.picking'].search([
                    ('sale_id', '=', order.id),
                    ('state', '=', 'done')
                ])
                if pickings:
                    uninvoiced = True
                    break

            partner.has_uninvoiced_stock_picking = uninvoiced
    
    
    def action_recompute_uninvoiced_stock_picking(self):
        """Recompute the 'has_uninvoiced_stock_picking' for selected partners."""
        for partner in self:
            partner._compute_has_uninvoiced_stock_picking()