from odoo import api, fields, models,exceptions,_
from odoo.tools.float_utils import float_round, float_compare, float_is_zero


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"


    def unlink(self):
        if self:
            self.state = 'draft'
        res = super(StockMoveLine, self).unlink()
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"


    def picking_cancel(self):
        if self.user_has_groups('stock_cancel_app.group_show_cancel_stock_picking'):
            stock_id =self.env['stock.picking'].browse(self._context.get('active_ids'))
            for rec in stock_id:
                rec.with_context({'Flag':True}).action_cancel()

    def picking_draft(self):
        if self.user_has_groups('stock_cancel_app.group_show_cancel_stock_picking'):
            stock_id =self.env['stock.picking'].browse(self._context.get('active_ids'))
            for rec in stock_id:
                rec.with_context({'Flag':True}).action_cancel()
                rec.state = 'draft'
                for move in rec.move_ids_without_package :
                    move.write({'state':'draft'})
    
    def picking_delete(self):
        if self.user_has_groups('stock_cancel_app.group_show_cancel_stock_picking'):
            stock_id =self.env['stock.picking'].browse(self._context.get('active_ids'))
            for rec in stock_id:
                rec.with_context({'Flag':True}).action_cancel()
            stock_id.unlink()


    def action_cancels(self):
        if self.company_id.stock_picking_type == 'cancel':
            self.action_cancel()
        if self.company_id.stock_picking_type == 'draft':
            self.action_cancel()
            self.write({'state':'draft'})
            for move in self.move_ids_without_package :
                move.write({'state':'draft'})
        if self.company_id.stock_picking_type == 'delete':
            self.with_context({'Flag':True}).action_cancel()
            self.unlink()
            return {
                    'name': _('Inventory Overview'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.picking',
                    'view_type':'form',
                    'view_mode' : 'tree',
                    'res_id': self.id,
                }

    def action_cancel(self):        
        quant_obj= self.env['stock.quant']
        moves = self.env['account.move']
        return_picking_obj = self.env['stock.return.picking']
        account_move_obj=self.env['account.move']
        for picking in self:
            if self.env.context.get('Flag',False) and picking.state =='done':
                account_moves=picking.move_lines
                return_pickings = return_picking_obj.search([('picking_id','=',picking.id)])
                if return_pickings and return_pickings:
                    pass
                for move in account_moves:
                    if move.state=='cancel':
                        continue
                    landed_cost_rec =[]
                    try:
                        landed_cost_rec= self.env['stock.landed.cost'].search(
                            [('picking_ids', '=', picking.id), ('state', '=', 'done')])
                    except :
                        pass
                    if landed_cost_rec:           
                        raise exceptions.Warning('This Delivery is set in landed cost record %s you need to delete it fisrt then you can cancel this Delivery'%','.join(landed_cost_rec.mapped('name')))
                    if move.state == "done" and move.product_id.type == "product":
                        for move_line in move.move_line_ids:
                            quantity = move_line.product_uom_id._compute_quantity(move_line.qty_done, move_line.product_id.uom_id)
                            quant_obj._update_available_quantity(move_line.product_id, move_line.location_id, quantity)
                            quant_obj._update_available_quantity(move_line.product_id, move_line.location_dest_id, quantity * -1)
                    if move.procure_method == 'make_to_order' and not move.move_orig_ids:
                        move.state = 'waiting'
                    elif move.move_orig_ids and not all(orig.state in ('done', 'cancel') for orig in move.move_orig_ids):
                        move.state = 'waiting'
                    else:
                        move.state = 'confirmed'
                    siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
                    if move.propagate_cancel:
                        if all(state == 'cancel' for state in siblings_states):
                            move.move_dest_ids._action_cancel()
                    else:
                        if all(state in ('done', 'cancel') for state in siblings_states):
                            move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                        move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
                    account_moves = account_move_obj.search([('stock_move_id', '=', move.id)])
                    if account_moves:
                        for account_move in account_moves:
                            account_move.button_cancel()
                            account_move.unlink()
        res=super(StockPicking,self).action_cancel()
        return res
               