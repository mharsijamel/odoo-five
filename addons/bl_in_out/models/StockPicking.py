from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def action_picking_tree_in(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('picking_type_id.code', '=', 'incoming')]
        return action

    @api.model
    def action_picking_tree_out(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('picking_type_id.code', '=', 'outgoing')]
        return action
