from odoo import models, fields, api, _
import time
from datetime import datetime
from odoo.exceptions import UserError
from .amount_to_text_fr import amount_to_text_fr

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
    treasury_ids = fields.Many2many('account.treasury', 'account_vesement_traite_treasury_rel', 'vesement_id',
                                    'treasury_id',
                                    'Associated Document', domain="[('type_transaction', '=', 'receipt')]",
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
        vals = {
            'ref': self.name,
            'journal_id': self.bank_target.journal_id.id,
            'narration': False,
            'date': self.date_vesement,
            'line_ids': [],
        }

        name = self.bank_target.acc_number
        if self.bank_target.bank_name:
            name = self.bank_target.bank_name
        move_line1 = {
            'name': "VERSEMENT [" + name + "] N:" + self.number or '/',
            'company_id': self.bank_target.journal_id.company_id.id,
            'debit': 0,
            'credit': self.amount,
            'account_id': self.journal_id.default_debit_account_id.id,
            'date': self.date_vesement,
        }
        vals['line_ids'].append([0, False, move_line1])

        move_line2 = {
            'name': "VERSEMENT [" + name + "] N:" + self.number or '/',
            'company_id': self.bank_target.journal_id.company_id.id,
            'debit': self.amount,
            'credit': 0,
            'account_id': self.bank_target.journal_id.default_credit_account_id.id,
            'date': self.date_vesement,
        }
        vals['line_ids'].append([0, False, move_line2])
        self.move_id = self.env['account.move'].create(vals)
        self.move_id.post()

    def button_validate(self):
        if len(self.treasury_ids) == 0:
            raise UserError(_('no treasury line !'))
        for treasury in self.treasury_ids:
            if treasury.state != 'in_cash':
                raise UserError(_('Document number %s for %s is not in cash !') % (
                    treasury.name, treasury.partner_id.name))
            treasury.state = 'versed'
            treasury.bank_target = self.bank_target.id
        self.state = 'valid'
        self.action_move_line_create()
        self.amount_in_word = amount_to_text_fr(self.amount, currency='Dinars')

    def button_cancel(self):
        for treasury in self.treasury_ids:
            if treasury.state != 'versed':
                raise UserError(_('Document number %s for %s is not versed !') % (
                    treasury.name, treasury.partner_id.name))
            treasury.state = 'in_cash'
            treasury.bank_target = False
        #######################################
        self.refresh()
        self.move_ids.remove_move_reconcile()
        #######################################
        self.move_id.button_cancel()
        self.move_id.unlink()
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('account.vesement.traite') or 'New'
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
                                                       ('maturity_date', '<=', self.date_to)])

            # ('type_transaction', '=', 'receipt')

            self.treasury_ids = [(6, 0, [x.id for x in inv])]

    @api.onchange('bank_target')
    def onchange_bank(self):
        self.journal_id = self.bank_target and self.bank_target.journal_id.id or False