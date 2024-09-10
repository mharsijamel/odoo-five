from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    move_type = fields.Selection(
        [('in', 'In'), ('out', 'Out')],
        string='Move Type',
        compute='_compute_move_type'
    )

    def _compute_move_type(self):
        for line in self:
            if line.location_id.usage == 'internal' and line.location_dest_id.usage != 'internal':
                line.move_type = 'out'
            elif line.location_id.usage != 'internal' and line.location_dest_id.usage == 'internal':
                line.move_type = 'in'
            else:
                line.move_type = False
