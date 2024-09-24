from odoo import models, fields, api

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

    def _compute_treasury_state(self):
        for line in self:
            treasury = self.env['account.treasury'].search([('move_line_id', '=', line.id)], limit=1)
            if treasury:
                line.treasury_state = treasury.state
            else:
                line.treasury_state = False
