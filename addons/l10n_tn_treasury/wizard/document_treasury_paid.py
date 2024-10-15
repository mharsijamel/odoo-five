from odoo import fields, models, api
from odoo.exceptions import UserError


class DocumentTreasuryPaid(models.TransientModel):
    _name = "document.treasury.paid"
    _description = "Paid Check/Treaty Wizard"

    check_id = fields.Many2one('account.treasury', string="Numéro Chèque/traite", required=True, ondelete="cascade")
    partner_id = fields.Many2one('res.partner', string="Holder", required=True)
    currency_id = fields.Many2one('res.currency', string="Devise")
    company_id = fields.Many2one('res.company', related='check_id.company_id')
    amount = fields.Float(string='Total', digits='Product Price', required=True, )
    date = fields.Date(string='Date', required=True)
    journal_target = fields.Many2one('account.journal', 'Journal Target',
                                     domain="[('type','in', ['bank', 'cash']), ('is_retenuachat','=',False), ('is_retenuachat','=',False), ('is_retenuvente','=',False)]")
    journal_type = fields.Selection(related="journal_target.type")
    payment_ref = fields.Char('Document Reference')
    action = fields.Selection([
        ('reverse', 'Re-verse'),
        ('cancel', 'Cancel')
    ], string='Action', required=True, default='reverse')
    
    def button_confirm(self):
        self.ensure_one()
        if self.action == 'reverse':
            #use same payment_id, just change move_line_id for treasury state listening and make transfer from impaid journal to bank journal
            self._reverse_move()
        elif self.action == 'cancel':
            #cancel payment and move line and treasury and unlink payment and invoice if it is
            self._cancel_move()
        return {'type': 'ir.actions.act_window_close'}

    def _reverse_move(self):
        if self.check_id.payment_type == 'inbound':
            if self.check_id.journal_id.incash_check:
                journal_id = self.env['account.journal'].sudo().search(
                    [('temporary_bank_journal', '=', True), ('inpayed_check', '=', True)], limit=1)
            elif self.check_id.journal_id.incash_treaty:
                journal_id = self.env['account.journal'].sudo().search(
                    [('temporary_bank_journal', '=', True), ('inpayed_treaty', '=', True)], limit=1)
            else:
                raise UserError(_("The journal type is not supported for this operation."))
            if not journal_id:
                raise UserError(_("Please configure a journal for paid checks/treaties."))
            move_vals = {
                'ref': f"{self.check_id.name} - Reverse",
                'journal_id': self.journal_target.id,
                'date': self.date,
                'line_ids': [
                    (0, 0, {
                        'name': f"Reverse: {self.check_id.name} - {self.check_id.holder.name}",
                        'account_id': journal_id.default_account_id.id,
                        'partner_id': self.check_id.holder.id,
                        'debit': 0,
                        'credit': self.check_id.amount,
                    }),
                    (0, 0, {
                        'name': f"Reverse: {self.check_id.name} - {self.check_id.holder.name}",
                        'account_id': self.journal_target.suspense_account_id.id,
                        'partner_id': self.check_id.holder.id,
                        'debit': self.check_id.amount,
                        'credit': 0,
                    }),
                ],
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            #i didn't reconcile because i used default_account_id of impaid journal first time
            self.check_id.write({
                'state': 'versed',
                'move_line_id': move.line_ids.filtered(lambda l: l.account_id == self.journal_target.suspense_account_id).id,
            })

    def _cancel_move(self):
        if self.check_id.payment_id:
            payment = self.check_id.payment_id
            # Remove reconciliation
            for line in payment.move_id.line_ids:
                if line.account_id.reconcile:
                    line.remove_move_reconcile()
            # Update the treasury record
            self.check_id.write({
                'state': 'cancel',
                'move_line_id': False,
            })
            # Cancel the payment
            payment.action_draft()
            payment.action_cancel()
            # Cancel the associated move if it exists
            if self.check_id.move_id:
                self.check_id.move_id.button_draft()
                self.check_id.move_id.button_cancel()
        else:
            raise UserError(_("No payment found for this treasury record."))