from odoo import models, fields, api
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)
class AccountMoveLineCharge(models.Model):
    _name = 'account.move.line.charge'
    _description = 'Charges for Account Move'

    name = fields.Char(string='Name', required=True)
    note = fields.Char(string='Note', required=True)
    amount = fields.Float(string='Montant (En Moannie Principale)', required=True)
    move_id = fields.Many2one('account.move', string='Move', ondelete='cascade')

    @api.model
    def create(self, vals):
        _logger.info(f"Creating AccountMoveLineCharge with vals: {vals}")
        res = super(AccountMoveLineCharge, self).create(vals)
        res.move_id.invoice_line_ids._compute_cost_product()
        return res

    def write(self, vals):
        _logger.info(f"Writing AccountMoveLineCharge with vals: {vals}")
        res = super(AccountMoveLineCharge, self).write(vals)
        self.mapped('move_id.invoice_line_ids')._compute_cost_product()
        return res

    def unlink(self):
        _logger.info(f"Unlinking AccountMoveLineCharge with ids: {self.ids}")
        moves = self.mapped('move_id')
        res = super(AccountMoveLineCharge, self).unlink()
        moves.mapped('invoice_line_ids')._compute_cost_product()
        return res
