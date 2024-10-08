from odoo import models, fields, api, _
import time
from datetime import datetime
from odoo.exceptions import UserError
from .amount_to_text_fr import amount_to_text_fr
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)



class AccountInstallmentTrait(models.Model):
    _name = 'account.installment.trait'
    _description = 'Vesement traite'
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
    treasury_ids = fields.Many2many('account.treasury', 'account_vesement_traite_treasury_rel', 'vesement_id', 'treasury_id',
                                    'Associated Document', domain="[('type_transaction', '=', 'receipt'), ('journal_id', '=', journal_id.id)]",
                                    readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float(string='Total', digits='Product Price', readonly=True, compute='_compute_amount')
    amount_in_word = fields.Char("Amount in Word")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    move_id = fields.Many2one('account.move', 'Account Entry', copy=False)
    move_ids = fields.One2many(related='move_id.line_ids', relation='account.move.line', string='Journal Items',
                               readonly=True)
    note = fields.Text('Notes')
    number = fields.Char('Number', required=1, readonly=True, states={'draft': [('readonly', False)]},
                         compute="_compute_treasury_number")
    expected = fields.Boolean('Expected effect')
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
                    'name': "Traite[" + line.holder.name + "]N:[" + line.name + "]DV:" + str(
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
                    'name': "Traite[" + line.holder.name + "]N:[" + line.name + "]DV:" + str(
                        line.maturity_date) or '/',
                    'debit': 0,
                    'credit': line.amount,
                    'partner_id': line.holder.id,
                    'account_id': line.payment_id.journal_id.suspense_account_id.id,
                    'date': vesement.date_vesement,
                }
                move['line_ids'].append([0, False, credit])

            self.move_id = self.env['account.move'].create(move)
            self.move_id.action_post()
            for line in vesement.treasury_ids:
                _logger.info('move id %s', self.move_id.id)
                
                if line.payment_type == 'inbound':
                    move_line = self.move_id.line_ids.filtered(
                        lambda l: (l.debit == line.amount) 
                                and l.partner_id.id == line.holder.id
                    )
                    move_line2 = self.move_id.line_ids.filtered(
                        lambda l: (l.credit == line.amount) 
                                and l.partner_id.id == line.holder.id
                    )
                elif line.payment_type == 'outbound':
                    move_line = self.move_id.line_ids.filtered(
                        lambda l: (l.credit == line.amount) 
                                and l.partner_id.id == line.holder.id
                    )
                    move_line2 = self.move_id.line_ids.filtered(
                        lambda l: (l.debit == line.amount) 
                                and l.partner_id.id == line.holder.id
                    )
                
                _logger.info('payment_id %s', line.payment_id)
                if line.payment_id:
                    payment = self.env['account.payment'].browse(line.payment_id.id)
                    if payment:
                        _logger.info('payment %s', payment)
                        # Find move lines to reconcile
                        lines_to_reconcile = payment.move_id.line_ids.filtered(
                            lambda l: l.account_id == payment.outstanding_account_id and not l.reconciled
                        )

                        _logger.info('lines_to_reconcile1 %s', lines_to_reconcile)
                        lines_to_reconcile |= move_line2  # Add the current move line

                        _logger.info('lines_to_reconcile1 %s', lines_to_reconcile)

                        # Perform reconciliation
                        lines_to_reconcile.reconcile()
                        payment.write({
                            'is_reconciled': True,
                            'is_matched': True,
                        })

                        _logger.info('reconciled ok ')

                    else:
                        _logger.warning(f"No matching payment found for payment ID: {line.payment_id.id}")
 
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
                raise UserError(_('Document number %s est déjà versé') % (
                    treasury.name))
            treasury.state = 'versed'
            treasury.bank_target = self.bank_target.id
            _logger.info('Bank target for treasury %s', self.bank_target.id)
        self.state = 'valid'
        self.action_move_line_create()
        self.amount_in_word = amount_to_text_fr(self.amount, currency='Dinars')

    def button_cancel(self):
        for treasury in self.treasury_ids:
            if treasury.state != 'versed':
                raise UserError(_('Document number %s is not versed !') % (
                    treasury.name))
            _logger.info('treasury 1')    
            # Restore payment state if exists
            if treasury.payment_id:
                payment = self.env['account.payment'].browse(treasury.payment_id.id)
                if payment:
                    # Find reconciled move lines
                    reconciled_lines = payment.move_id.line_ids.filtered(
                        lambda l: l.account_id == payment.outstanding_account_id and l.reconciled
                    )
                    
                    # Remove reconciliation
                    if reconciled_lines:
                        reconciled_lines.remove_move_reconcile()
                    
                    # Reset payment state
                    payment.write({
                        'is_reconciled': False,
                        'is_matched': False,
                    })
            _logger.info('treasury 2')            
            # Reset treasury state
            treasury.state = 'in_cash'
            treasury.bank_target = False
            _logger.info('treasury 3')    
            # Clear move_line reference if exists
            if treasury.move_line_id:
                treasury.move_line_id = False
            _logger.info('treasury 4')    
        # Cancel and delete the move
        if self.move_id:
            self.move_id.button_draft()  # First set to draft before canceling
            self.move_id.button_cancel()
            self.move_id.with_context(force_delete=True).unlink()
        _logger.info('treasury 5')        
        self.move_id = False
        self.state = 'cancel'



    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('account.installment.trait') or 'New'
        new_id = super(AccountInstallmentTrait, self).create(vals)
        new_id.message_post(body=_("Vesement created"))
        return new_id

    def unlink(self):
        for vesement in self:
            if vesement.state != 'draft':
                raise UserError(_('You cannot delete this vesement !'))
        return super(AccountInstallmentTrait, self).unlink()

    @api.onchange('date_from', 'date_to')
    def onchange_date(self):
        if not self.date_from or not self.date_to:
            self.treasury_ids = []
        else:
            inv = self.env['account.treasury'].search([('state', '=', 'in_cash'),
                                                       ('maturity_date', '>=', self.date_from),
                                                     # ('payment_type', '=', 'inbound'),
                                                       ('maturity_date', '<=', self.date_to),
                                                       ('journal_id.incash_treaty', '=', True)])

            # ('type_transaction', '=', 'receipt')

            self.treasury_ids = [(6, 0, [x.id for x in inv])]

    @api.onchange('bank_target')
    def onchange_bank(self):
        self.journal_id = self.bank_target and self.bank_target.journal_id.id or False