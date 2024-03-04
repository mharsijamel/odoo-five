# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date



class exchange_document_line(models.Model):
    _name = "account.exchange.document.line"
    _description = "Exchange Document Line"

    document_id = fields.Many2one('account.treasury', 'Document', readonly=False)
    exchange_document_id = fields.Many2one('account.exchange.document', 'Exchange Document', ondelete="set null")
    # partner_id = fields.Many2one('res.partner', 'Partner', readonly=True, related="document_id.partner_id")
    holder = fields.Many2one('res.partner','Holder', readonly=True, related="document_id.holder")
    amount = fields.Float('Amount', readonly=True, related="document_id.amount")
    maturity_date = fields.Date('Maturity Date', readonly=True, related="document_id.maturity_date")
    bank_origin = fields.Many2one('res.bank', 'Bank Origin', readonly=True, related="document_id.bank_origin")
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True, related='exchange_document_id.company_id')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, related='company_id.currency_id',
                                  store=True)


class exchange_document(models.Model):
    _name = "account.exchange.document"
    _description = "Exchange Document"

    name = fields.Char('Document ID')
    bank_source_ids = fields.Many2many('res.bank')
    journal_target = fields.Many2one('account.journal', 'Journal Target', required=True,
                                     domain="[('type','in', ['bank']), ('temporary_bank_journal','=',False), ('is_retenuachat','=',False), ('is_retenuvente','=',False)]")
    journal_id = fields.Many2one('account.journal', 'Journal Source', domain="[('temporary_bank_journal','=',True)]")

    line_ids = fields.One2many('account.exchange.document.line', 'exchange_document_id')

    date_start = fields.Date('Date Start', default=date.today())
    date_stop = fields.Date('Date Stop', default=date.today())
    amount = fields.Monetary('Amount', compute="_get_total", digits='Product Price')
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True,
                                 help="Company related to this treasury", default=lambda self: self.env.user.company_id)
    move_id = fields.Many2one('account.move', 'Account Move', readonly=True)
    document_state = fields.Selection([('in_cash', 'In Cash'), ('versed', 'Versed')], string="Document State", default="versed")
    state = fields.Selection([('draft', 'Open'), ('valid', 'Valid'), ('cancel', 'Cancelled')], 'State', required=True, readonly=True, index=1, default='draft')
    bank_commission = fields.Float('Bank Commission', digits='Product Price')
    bank_commission_total = fields.Float('Bank Commission Total', compute="_get_bank_commission_total", digits='Product Price')
    bank_commission_account = fields.Many2one('account.account', 'Bank Commission Account')
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, related='company_id.currency_id', store=True)

    @api.onchange('bank_source_ids', 'date_start', 'date_stop', 'journal_id', 'company_id', 'document_state')
    def onchange_journal(self):
        condition = [
            ('maturity_date', '<=', self.date_stop),
            ('maturity_date', '>=', self.date_start),
            ('journal_id', '=', self.journal_id.id),
            ('company_id', '=', self.company_id.id),
            ('state', '=', self.document_state)]
        if len(self.bank_source_ids):
            condition.append(('bank_origin', 'in', self.bank_source_ids.ids))
        document_ids = self.env['account.treasury'].search(condition)
        print(document_ids)
        res = []
        for id in document_ids:
            res.append([0, 0, {'document_id': id}])
        self.line_ids = res

    def button_validate(self):
        partner = self.line_ids.mapped('holder')
        vals = {'ref': self.name,
                'journal_id': self.journal_target.id,
                'narration': False,
                'date': date.today(),
                # 'partner_id': partner.id,
                'to_check': False,
                'line_ids': [], }
        if self.bank_commission_total != 0:
            if self.bank_commission_account:
                # vals for bank commission move
                bank_commission_move_lin = [0, False,
                                            {'analytic_account_id': False,
                                             # 'tax_code_id': False,
                                             # 'tax_amount': 0,
                                             'name': self.name,
                                             'journal_id': self.journal_target.id,
                                             'company_id': self.company_id.id,
                                             'currency_id': False,
                                             'credit': 0,
                                             'date_maturity': False,
                                             'debit': self.bank_commission_total,
                                             'date': date.today(),
                                             'amount_currency': 0,
                                             # 'partner_id': partner.id,
                                             'account_id': self.bank_commission_account.id}]
                vals['line_ids'].append(bank_commission_move_lin)

                credit_commission = [0, False,
                                     {'analytic_account_id': False,
                                      # 'tax_code_id': False,
                                      # 'tax_amount': 0,
                                      'name': self.name,
                                      'journal_id': self.journal_id.id,
                                      'company_id': self.company_id.id,
                                      'currency_id': False,
                                      'credit': self.bank_commission_total,
                                      'date_maturity': False,
                                      'debit': 0,
                                      'date': date.today(),
                                      'amount_currency': 0,
                                      # 'partner_id': partner.id,
                                      'account_id': self.journal_target.default_account_id.id}]

                vals['line_ids'].append(credit_commission)
            else:
                raise exceptions.ValidationError(
                    _("If the amount of the bank commission is defined you must define the account for this move"))

        # vals for move
        # debit = [0, False,
        #          {'analytic_account_id': False,
        #           # 'tax_code_id': False,
        #           # 'tax_amount': 0,
        #           'name': self.name,
        #           'journal_id': self.journal_target.id,
        #           'company_id': self.company_id.id,
        #           'currency_id': False,
        #           'credit': 0,
        #           'date_maturity': False,
        #           'debit': self.amount,
        #           'date': date.today(),
        #           'amount_currency': 0,
        #           'partner_id': partner.id,
        #           'account_id': self.journal_target.default_account_id.id}]
        # credit = [0, False,
        #           {'analytic_account_id': False,
        #            # 'tax_code_id': False,
        #            # 'tax_amount': 0,
        #            'name': self.name,
        #            'journal_id': self.journal_id.id,
        #            'company_id': self.company_id.id,
        #            'currency_id': False,
        #            'credit': self.amount,
        #            'date_maturity': False,
        #            'debit': 0,
        #            'date': date.today(),
        #            'amount_currency': 0,
        #            'partner_id': partner.id,
        #            'account_id': self.journal_id.default_account_id.id}]
        #
        #
        # vals['line_ids'].append(debit)
        # vals['line_ids'].append(credit)
        move_id = self.move_id.id
        if move_id:
            self.move_id = self.move_id.write(vals)
            self.move_id.action_post()
        else:
            self.move_id = self.env['account.move'].create(vals)
            self.move_id.action_post()

        for line in self.line_ids:
            if self.document_state == 'in_cash':
                line.document_id.state = 'versed'
                line.document_id.journal_id = self.journal_target.id
            if self.document_state == 'versed':
                line.document_id.state = 'paid'
                line.document_id.journal_id = self.journal_target.id
        self.state = 'valid'

    def button_cancel(self):
        for id in self.ids:
            document = self.browse(id)
            self.pool.get('account.move').unlink(document.move_id)
        return self.write({'state': 'cancel'})

    def button_draft(self):
        return self.write({'state': 'draft'})

    @api.depends('line_ids')
    def _get_total(self):
        total = 0.0
        for line in self.line_ids:
            total += line.amount
        self.amount = total

    @api.depends('bank_commission', 'line_ids')
    def _get_bank_commission_total(self):
        self.bank_commission_total = len(self.line_ids) * self.bank_commission

