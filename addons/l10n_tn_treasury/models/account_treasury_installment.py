from odoo import api, fields, models, _
from odoo import models, fields, api, _
import time
from datetime import datetime
from odoo.exceptions import UserError
from .amount_to_text_fr import amount_to_text_fr
import logging

_logger = logging.getLogger(__name__)

class AccountTreasuryInstallment(models.Model):

    _name = 'account.treasury.installment'

    _description = 'Cash Vesement'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char('Reference', copy=False, readonly=True, select=True)
    date_vesement = fields.Date(string='Vesement Date', default=lambda *a: time.strftime('%Y-%m-%d'),
                                readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    journal_target = fields.Many2one('account.journal', 'Journal Target', readonly=True,
                                     states={'draft': [('readonly', False)]}, domain=[('type', '=', 'bank')])
    bank_target = fields.Many2one('res.partner.bank', 'Target Bank', readonly=True,
                                  states={'draft': [('readonly', False)]}, domain=[('company_id', '<>', False)])
    journal_source = fields.Many2one('account.journal', 'Journal Source', readonly=True,
                                     states={'draft': [('readonly', False)]}, domain=[('type', '=', 'cash')])
    amount = fields.Float(string='Total', digits='Product Price', required=True, readonly=True,
                          states={'draft': [('readonly', False)]})
    amount_in_word = fields.Char("Amount in Word")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, readonly=True,
                                 states={'draft': [('readonly', False)]})
    move_id = fields.Many2one('account.move', 'Account Entry', copy=False)
    move_ids = fields.One2many(related='move_id.line_ids', relation='account.move.line', string='Journal Items',
                               readonly=True)
    note = fields.Text('Notes')
    number = fields.Char('Number', required=1, readonly=True, states={'draft': [('readonly', False)]}, default=1)
    account_id = fields.Many2one('account.account', 'Account', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Open'),
        ('valid', 'Validate'),
        ('cancel', 'Cancel'),
    ], 'State', required=True, readonly=True, select=1, default='draft', track_visibility='onchange')

    @api.onchange('bank_target')
    def onchange_bank(self):
        self.journal_target = self.bank_target and self.bank_target.journal_id.id or False


    # to test
    @api.onchange('bank_target')
    def onchange_journal(self):
        self.account_id = self.journal_target.default_account_id or False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('account.treasury.installment') or 'New'
        new_id = super(AccountTreasuryInstallment, self).create(vals)
        new_id.message_post(body=_("Vesement created"))
        return new_id

    def unlink(self):
        for vesement in self:
            if vesement.state != 'draft':
                raise UserError(_('You cannot delete this cash vesement !'))
        return super(AccountTreasuryInstallment, self).unlink()

    def button_draft(self):
        self.state = 'draft'

    def action_move_line_create(self):
        AccountMoveLine = self.env['account.move.line']
        _logger.info("move line %s", AccountMoveLine)
        domain = [
            ('account_id', '=', self.journal_source.default_account_id.id),
            ('date', '<=', self.date_vesement),
        ]
        balance = sum(AccountMoveLine.search(domain).mapped('balance'))
        _logger.info("balance %s", balance)
        if balance < self.amount:
            raise UserError(_('Insufficient balance in the source journal. Available balance: %s') % balance)
        vals = {
            'ref': self.name,
            'journal_id': self.journal_target.id,
            'narration': False,
            'date': self.date_vesement,
            'line_ids': [],
        }

        name = self.bank_target.acc_number
        if self.bank_target.bank_name:
            name = self.bank_target.bank_name
        move_line1 = {
            'name': "VERSEMENT [" + name + "] N:" + self.number or '/',
            'company_id': self.journal_target.company_id.id,
            'debit': 0,
            'credit': self.amount,
            'account_id': self.journal_source.default_account_id.id,
            'date': self.date_vesement,
        }
        vals['line_ids'].append([0, False, move_line1])


        move_line2 = {
            'name': "VERSEMENT [" + name + "] N:" + self.number or '/',
            'company_id': self.journal_target.company_id.id,
            'debit': self.amount,
            'credit': 0,
            'account_id': self.journal_target.withdrawal_account.id,
            'date': self.date_vesement,
        }
        vals['line_ids'].append([0, False, move_line2])

        move_line3 = {
            'name': "VERSEMENT [" + name + "] N:" + self.number or '/',
            'company_id': self.journal_target.company_id.id,
            'debit': 0,
            'credit': self.amount,
            'account_id': self.journal_target.withdrawal_account.id,
            'date': self.date_vesement,
        }
        vals['line_ids'].append([0, False, move_line3])


        move_line4 = {
            'name': "VERSEMENT [" + name + "] N:" + self.number or '/',
            'company_id': self.journal_target.company_id.id,
            'debit': self.amount,
            'credit': 0,
            'account_id': self.journal_target.default_account_id.id,
            'date': self.date_vesement,
        }
        vals['line_ids'].append([0, False, move_line4])


        self.move_id = self.env['account.move'].create(vals)
        self.move_id.action_post()

    def button_validate(self):
        if self.amount > 0.0:
            self.amount_in_word = amount_to_text_fr(self.amount, currency='Dinars')
            self.state = 'valid'
            self.action_move_line_create()
            return True
        else:
            raise UserError(_('Le Montant de versement doit être supérieur à Zéro'))
    
    def button_cancel(self):
        self.move_id.button_cancel()
        self.move_id.unlink()
        self.state = 'cancel'
        return True
