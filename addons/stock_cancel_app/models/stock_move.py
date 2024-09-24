from odoo import api, fields, models,exceptions
from odoo.tools.float_utils import float_round, float_compare, float_is_zero

class StockMove(models.Model):
    _inherit = 'stock.move'

    def cancel_order(self):
        if self.user_has_groups('stock_cancel_app.group_cancel_stock_move'):
            stock_id = self.env['stock.move'].browse(self._context.get('active_ids'))
            for rec in stock_id:
                rec.state = 'draft'
                rec._action_cancel()
                rec.state = 'cancel'

    def draft_order(self):
        if self.user_has_groups('stock_cancel_app.group_cancel_stock_move'):
            stock_id = self.env['stock.move'].browse(self._context.get('active_ids'))
            for rec in stock_id:
                rec.state = 'draft'
                rec._action_cancel()
                rec.state = 'draft'

    def delete_order(self):
        if self.user_has_groups('stock_cancel_app.group_cancel_stock_move'):
            stock_id = self.env['stock.move'].browse(self._context.get('active_ids'))
            for rec in stock_id:
                rec.state = 'draft'
                rec._action_cancel()
                rec.state = 'draft'
            stock_id.unlink()               

    
    def _action_cancel(self):
        for move in self:
            move._do_unreserve()
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate_cancel:
                # only cancel the next move if all my siblings are also cancelled
                if all(state == 'cancel' for state in siblings_states):
                    move.move_dest_ids._action_cancel()
            else:
                if all(state in ('done', 'cancel') for state in siblings_states):
                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                    move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})          
            if move.state == 'done':
                stock_move_id = self.env['stock.move'].sudo().search([('product_id','=',move.product_id.id),('reference','=',move.scrap_ids.name)])
                for move_id in stock_move_id:
                    for line in move_id.move_line_ids:
                        stock_quant_id = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',line.location_id.id),('lot_id','=',line.lot_id.id)])
                        if stock_quant_id:
                            quant_qty = stock_quant_id[0].quantity
                            stock_quant_id[0].quantity = quant_qty + move.product_uom_qty
            if move.account_move_ids:
                move.account_move_ids.filtered(lambda x: x.state == 'posted').sudo().button_cancel()
                move.account_move_ids.sudo().unlink()
            self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})

        else:
            if any(move.state == 'done' for move in self):
                raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'.'))
            for move in self:
                if move.state == 'cancel':
                    continue
                move._do_unreserve()
                siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
                if move.propagate_cancel:
                    # only cancel the next move if all my siblings are also cancelled
                    if all(state == 'cancel' for state in siblings_states):
                        move.move_dest_ids.filtered(lambda m: m.state != 'done')._action_cancel()
                else:
                    if all(state in ('done', 'cancel') for state in siblings_states):
                        move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                        move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
                        
            self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
        return True