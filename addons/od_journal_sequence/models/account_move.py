# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging

# Define the logger
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    name = fields.Char(string='Number', required=True, readonly=False, copy=False, default='/')

    def _get_sequence(self):
        _logger.info('sequence 1')
        self.ensure_one()
        journal = self.journal_id
        if self.move_type in ('entry', 'out_invoice', 'in_invoice', 'out_receipt', 'in_receipt') or not journal.refund_sequence:
            sequence= journal.sequence_id
            _logger.info('sequence 2')
        else:
            sequence= journal.refund_sequence_id
            _logger.info('sequence 3')
        _logger.info('sequence %s found', self._get_payment_sequence())
        if not sequence:
            sequence= self._get_payment_sequence()
        return sequence

    def _get_payment_sequence(self):
        """
        Helper method to fetch the sequence from the associated payment model.
        """
        # Determine the correct sequence code based on the move type
        _logger.info('sequence 4 %s',self.move_type)
        if self.move_type in ('entry', 'in_invoice', 'in_receipt'):
            sequence_code = 'account.payment.supplier.invoice'
        elif self.move_type in ( 'out_invoice',  'out_receipt'):
            sequence_code = 'account.payment.customer.invoice'
        else:
            return None  # Return None if it's not an invoice type

        # Search for the sequence based on the code
        payment_sequence = self.env['ir.sequence'].search([('code', '=', sequence_code)], limit=1)

        # Return the found sequence or None if not found
        return payment_sequence

    def _post(self, soft=True):
        for move in self:
            if move.name == '/':
                sequence = move._get_sequence()
                if not sequence:
                    raise UserError(_('Please define a sequence on your journal.'))
                move.name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
        res = super(AccountMove, self)._post(soft=True)
        return res

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        self.name = '/'

    def _constrains_date_sequence(self):
        return
