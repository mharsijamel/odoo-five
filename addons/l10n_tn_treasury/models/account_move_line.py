from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    treasury_state = fields.Selection(
        [('in_cash', 'In Cash'),
         ('versed', 'Versed'),
         ('paid', 'Paid'),
         ('notice', 'Notice'),
         ('cancel', 'Cancelled')],
        string='Statut du Document',
        compute='_compute_treasury_state',
        store=True
    )

    @api.depends('matching_number','name')
    def _compute_treasury_state(self):
        
        all_move_lines = self.search([])
        for line in all_move_lines:
            treasury = self.env['account.treasury'].search([('move_line_id', '=', line.id)], limit=1)
            if treasury:
                line.treasury_state = treasury.state
            else:
                line.treasury_state = False
