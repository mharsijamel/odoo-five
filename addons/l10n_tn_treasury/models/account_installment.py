from odoo import models, fields, api, _
import time
from datetime import datetime
from odoo.exceptions import UserError
from .amount_to_text_fr import amount_to_text_fr


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
                                  states={'draft': [('readonly', False)]}, domain=[('company_id', '<>', False)])
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
                    'partner_id': line.partner_id.id,
                    'debit': line.amount,
                    'credit': 0,
                    'account_id': vesement.journal_id.default_account_id.id,
                    'date': vesement.date_vesement,
                }
                move['line_ids'].append([0, False, debit])

            for line in vesement.treasury_ids:
                credit = {
                    'name': "Cheque[" + line.holder.name + "]N:[" + line.name + "]DV:" + str(
                        line.maturity_date) or '/',
                    'debit': 0,
                    'credit': line.amount,
                    'partner_id': line.partner_id.id,
                    'account_id': line.payment_id.journal_id.default_account_id.id,
                    'date': vesement.date_vesement,
                }
                move['line_ids'].append([0, False, credit])

            self.move_id = self.env['account.move'].create(move)
            self.move_id.action_post()
            # account_move_lines_to_reconcile = self.env['account.move.line']
            # for treas in vesement.treasury_ids:
            #     account_move_lines_to_reconcile |= treas.payment_id.line_ids.filtered(
            #         lambda line: line.account_id.user_type_id.type == 'liquidity')
            # account_move_lines_to_reconcile |= self.move_id.line_ids.filtered(lambda line: line.credit > 0)
            # account_move_lines_to_reconcile.reconcile()

    def button_validate(self):
        if len(self.treasury_ids) == 0:
            raise UserError(_('no treasury line !'))
        for treasury in self.treasury_ids:
            if treasury.state != 'in_cash':
                raise UserError(_('Document number %s for %s is not in cash !') % (
                    treasury.name, treasury.holder.name))
            treasury.state = 'versed'
        self.amount_in_word = amount_to_text_fr(self.amount, currency='Dinars')
        self.state = 'valid'
        # self.action_move_line_create()

    def button_cancel(self):
        for treasury in self.treasury_ids:
            if treasury.state != 'versed':
                raise UserError(_('Document number %s for %s is not versed !') % (
                    treasury.name, treasury.holder.name))
            treasury.state = 'in_cash'
            treasury.bank_target = False
        self.state = 'cancel'

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


