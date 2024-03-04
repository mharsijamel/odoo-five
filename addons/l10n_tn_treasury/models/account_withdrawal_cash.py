from odoo import api, fields, models, _
import time
from datetime import datetime
from odoo.exceptions import UserError
from .amount_to_text_fr import amount_to_text_fr


class AccountWithdrawalCash(models.Model):
    _name = "account.withdrawal.cash"
    _description = 'Cash Withdrawal'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char('Reference', copy=False, readonly=True, select=True)
    date_withdrawal = fields.Date(string='Withdrawal Date', default=lambda *a: time.strftime('%Y-%m-%d'),
                                  readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    journal_target = fields.Many2one('account.journal', 'Journal Target', readonly=True,
                                     states={'draft': [('readonly', False)]}, domain=[('type', '=', 'cash')])
    number = fields.Char('Number', required=1, readonly=True, states={'draft': [('readonly', False)]}, default=1)
    bank_source = fields.Many2one('res.partner.bank', 'Target Bank', readonly=True,
                                  states={'draft': [('readonly', False)]}, domain=[('company_id', '<>', False)])
    journal_source = fields.Many2one('account.journal', 'Journal Source', readonly=True,
                                     states={'draft': [('readonly', False)]}, domain=[('type', '=', 'bank')])
    account_id = fields.Many2one('account.account', 'Account', readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float(string='Total', digits='Product Price', required=True, readonly=True,
                          states={'draft': [('readonly', False)]})
    amount_in_word = fields.Char("Amount in Word")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, readonly=True,
                                 states={'draft': [('readonly', False)]})
    move_id = fields.Many2one('account.move', 'Account Entry', copy=False)
    move_ids = fields.One2many(related='move_id.line_ids', relation='account.move.line', string='Journal Items',
                               readonly=True)
    note = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'Open'),
        ('valid', 'Validate'),
        ('cancel', 'Cancel'),
    ], 'State', required=True, readonly=True, select=1, default='draft', track_visibility='onchange')

    @api.onchange('bank_source')
    def onchange_bank(self):
        self.journal_source = self.bank_source and self.bank_source.journal_id.id or False


    # to test
    @api.onchange('journal_target')
    def onchange_journal(self):
        self.account_id = self.journal_target.default_account_id or False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('account.withdrawal.cash') or 'New'
        new_id = super(AccountWithdrawalCash, self).create(vals)
        new_id.message_post(body=_("Withdrawal created"))
        return new_id

    def unlink(self):
        for withdrawal in self:
            if withdrawal.state != 'draft':
                raise UserError(_('You cannot delete this cash withdrawal !'))
        return super(AccountWithdrawalCash, self).unlink()

    def button_draft(self):
        self.state = 'draft'

    def action_move_line_create(self):
        vals = {
            'ref': self.name,
            'journal_id': self.journal_target.id,
            'narration': False,
            'date': self.date_withdrawal,
            'line_ids': [],
        }

        move_line1 = {
            'name': "Retrait [" + self.bank_source.bank_name + "] N:" + self.number or '/',
            'company_id': self.journal_target.company_id.id,
            'debit': 0,
            'credit': self.amount,
            'account_id': self.journal_source.default_account_id.id,
            'date': self.date_withdrawal,
            'move_id': self.id,
            'journal_id': self.journal_source.id,
            'date_maturity': self.date_withdrawal
        }
        vals['line_ids'].append([0, False, move_line1])

        move_line2 = {
            'name': "Retrait [" + self.bank_source.bank_name + "] N:" + self.number or '/',
            'company_id': self.journal_target.company_id.id,
            'debit': self.amount,
            'credit': 0,
            'account_id': self.journal_target.default_account_id.id,
            'move_id': self.id,
            'journal_id': self.journal_source.id,
            'date': self.date_withdrawal,
            'date_maturity': self.date_withdrawal
        }
        vals['line_ids'].append([0, False, move_line2])
        self.move_id = self.env['account.move'].create(vals)
        self.move_id.post()

    def button_validate(self):
        if self.amount > 0.0:
            self.amount_in_word = amount_to_text_fr(self.amount, currency='Dinars')
            self.state = 'valid'
            self.action_move_line_create()
        else:
            raise UserError(_('Le Montant de retrait doit être supérieur à Zéro'))

    def button_cancel(self):
        self.move_id.button_cancel()
        self.move_id.unlink()
        self.state = 'cancel'