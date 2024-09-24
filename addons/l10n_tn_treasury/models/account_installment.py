from odoo import models, fields, api, _
import time
from datetime import datetime
from odoo.exceptions import UserError
from .amount_to_text_fr import amount_to_text_fr
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class AccountInstallment(models.Model):

    _name = 'account.installment'
    _description = 'Installment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char('Reference', copy=False, readonly=True, select=True)
    date_vesement = fields.Date(string='Vesement Date', default=datetime.now().strftime('%Y-%m-%d'),
                                readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    date_from = fields.Date(string='Start Date', default=datetime.now().strftime('%Y-%m-%d'),
                            readonly=True, states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='End Date', default=datetime.now().strftime('%Y-%m-%d'),
                          readonly=True, states={'draft': [('readonly', False)]})
    bank_target = fields.Many2one('res.partner.bank', 'Target Bank', readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  domain=[('company_id', '<>', False)])
    journal_id = fields.Many2one('account.journal', 'Journal', readonly=True, states={'draft': [('readonly', False)]},
                                 domain=[('type', '=', 'bank')])
    treasury_ids = fields.Many2many('account.treasury', 'account_vesement_treasury_rel', 'vesement_id', 'treasury_id',
                                    'Associated Document', domain="[('type_transaction', '=', 'receipt'), ('journal_id', '=', journal_id.id)]",
                                    readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float(string='Total', digits='Product Price', readonly=True, compute='_compute_amount')
    amount_in_word = fields.Char("Amount in Word")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    move_id = fields.Many2one('account.move', 'Account Entry', copy=False)
    move_ids = fields.One2many(related='move_id.line_ids', relation='account.move.line', string='Journal Items',
                               readonly=True)
    number = fields.Char('Number', required=1, readonly=True, states={'draft': [('readonly', False)]},
                         compute="_compute_treasury_number")
    note = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'Open'),
        ('valid', 'Validate'),
        ('cancel', 'Cancel'),
    ], 'State', required=True, readonly=True, select=1, default='draft', track_visibility='onchange')

    @api.depends('treasury_ids')
    def _compute_treasury_number(self):
        for rec in self:
            rec.number = len(rec.treasury_ids)

    def _compute_amount(self):
        for rec in self:
            rec.amount = sum(line.amount for line in rec.treasury_ids)

    def button_draft(self):
        self.state = 'draft'

    def action_move_line_create(self):
        for vesement in self:
            if vesement.move_id:
                continue
            # Create the account move record.
            move = {
                'journal_id': vesement.journal_id.id,
                'date': vesement.date_vesement,
                'ref': vesement.name,
                'line_ids': [],

            }
            for line in vesement.treasury_ids:
                debit = {
                    'name': "Cheque[" + line.holder.name + "]N:[" + line.name + "]DV:" + str(
                        line.maturity_date) or '/',
                    'partner_id': line.holder.id,
                    'debit': line.amount,
                    'credit': 0,
                    'account_id': vesement.journal_id.suspense_account_id.id,
                    'date': vesement.date_vesement,
                }
                move['line_ids'].append([0, False, debit])

            for line in vesement.treasury_ids:
                credit = {
                    'name': "Cheque[" + line.holder.name + "]N:[" + line.name + "]DV:" + str(
                        line.maturity_date) or '/',
                    'debit': 0,
                    'credit': line.amount,
                    'partner_id': line.holder.id,
                    'account_id': line.journal_id.suspense_account_id.id,
                    'date': vesement.date_vesement,
                }
                move['line_ids'].append([0, False, credit])

            self.move_id = self.env['account.move'].create(move)
            self.move_id.action_post()
            for line in vesement.treasury_ids:
                _logger.info('move id %s', self.move_id.id)
                move_line = self.move_id.line_ids.filtered(
                    lambda l: (l.debit == line.amount)  # Only credit lines
                              and l.partner_id.id == line.holder.id
                )
                if len(move_line) > 1:
                    _logger.warning(
                        f"Multiple matching move lines found for amount: {line.amount}, partner: {line.holder.id}")
                    # Select the correct move line based on additional criteria
                    move_line = move_line[0]
                if move_line:
                    line.move_line_id = move_line.id
                else:
                    _logger.warning(f"No matching move line found for amount: {line.amount}, partner: {line.holder.id}")


    def button_validate(self):
        if len(self.treasury_ids) == 0:
            raise UserError(_('no treasury line !'))
        for treasury in self.treasury_ids:
            if treasury.state != 'in_cash':
                raise UserError(_('Document number %s for %s is not in cash !') % (
                    treasury.name, treasury.holder.name))
            treasury.state = 'versed'
            treasury.bank_target = self.bank_target.id
            _logger.info('Bank target for treasury %s', self.bank_target.id)
        self.amount_in_word = amount_to_text_fr(self.amount, currency='Dinars')
        self.state = 'valid'
        self.action_move_line_create()
        #self._create_bank_statement()
    
    # def _create_bank_statement(self):
    #     for vesement in self:
    #         # Create the bank statement
    #         statement = {
    #             'journal_id': vesement.journal_id.id,
    #             'date': vesement.date_vesement,
    #             'name': _('Bank Statement %s') % vesement.name,
    #             'line_ids': [],
    #         }
    #
    #         # Calculate the starting balance
    #         account_move_lines = self.env['account.move.line'].search([
    #             ('account_id', '=', vesement.journal_id.default_account_id.id),
    #             ('date', '<', vesement.date_vesement),
    #         ])
    #
    #         # Calculate the starting balance
    #         last_statement = self.env['account.bank.statement'].search([
    #             ('journal_id', '=', vesement.journal_id.id),
    #             ('state', '=', 'posted'),
    #         ], order='date DESC', limit=1)
    #
    #         # Set starting balance based on the last bank statement or 0 if none exists
    #         balance_start = last_statement.balance_end if last_statement else 0.0
    #         balance_end = balance_start
    #
    #         for line in vesement.treasury_ids:
    #             # Determine transaction type based on amount sign
    #             if line.amount > 0:
    #                 transaction_type = 'debit'
    #             elif line.amount < 0:
    #                 transaction_type = 'credit'
    #             else:
    #                 transaction_type = 'other'
    #
    #             bank_statement_line = {
    #                 'move_id': False,  # Set as needed
    #                 'statement_id': False,  # Will be set after creating the statement
    #                 'sequence': False,  # Set as needed
    #                 'account_number': vesement.journal_id.default_account_id.name,
    #                 'partner_name': line.holder.name if line.holder else '',
    #                 'transaction_type': transaction_type,
    #                 'payment_ref': line.name or '',
    #                 'amount': line.amount,
    #                 'partner_id': line.holder.id if line.holder else False,
    #                 'is_reconciled': False,
    #             }
    #
    #             statement['line_ids'].append([0, False, bank_statement_line])
    #             balance_end += line.amount
    #
    #         # Create the statement
    #         created_statement = self.env['account.bank.statement'].create(statement)
    #         # Update the statement lines with the correct statement_id
    #         for line in created_statement.line_ids:
    #             line.write({'statement_id': created_statement.id})
    #         created_statement.write({'balance_start': balance_start})


    def button_cancel(self):
        for vesement in self:
            # Check if all related treasury lines are in the 'versed' state
            for treasury in vesement.treasury_ids:
                if treasury.state != 'versed':
                    raise UserError(_('Document number %s for %s is not versed!') % (
                        treasury.name, treasury.holder.name))
                # Reset the state of the treasury lines to 'in_cash'
                treasury.state = 'in_cash'
                treasury.bank_target = False  # Clear the bank target

            # Change state to cancel
            vesement.state = 'cancel'
            
            # Delete the associated bank statement
            if vesement.move_id:
                vesement.move_id.button_cancel()
                vesement.move_id.unlink()
            
            # Find and delete the associated bank statement
            statement = self.env['account.bank.statement'].search([
                ('journal_id', '=', vesement.journal_id.id),
                ('name', '=', _('Bank Statement %s') % vesement.name)
            ])

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('account.installment') or 'New'
        new_id = super(AccountInstallment, self).create(vals)
        new_id.message_post(body=_("Vesement created"))
        return new_id

    def unlink(self):
        for vesement in self:
            if vesement.state != 'draft':
                raise UserError(_('You cannot delete this vesement !'))
        return super(AccountInstallment, self).unlink()

    @api.onchange('date_from', 'date_to')
    def onchange_date(self):
        if self.date_from and self.date_to:
            inv = self.env['account.treasury'].search([('state', '=', 'in_cash'),
                                                       ('maturity_date', '>=', self.date_from),
                                                       ('maturity_date', '<=', self.date_to),
                                                       ('payment_type', '=', 'inbound'),
                                                       ('company_id', '=', self.company_id.id)])
            self.treasury_ids = [(6, 0, [x.id for x in inv])]

    @api.onchange('bank_target')
    def onchange_bank(self):
        self.journal_id = self.bank_target and self.bank_target.journal_id.id or False


