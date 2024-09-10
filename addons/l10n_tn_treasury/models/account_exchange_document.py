# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _, Command
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
    journal_id = fields.Many2one('account.journal', 'Journal Source', domain="[('type','in', ['bank']), ('temporary_bank_journal','=',False), ('is_retenuachat','=',False), ('is_retenuvente','=',False)]")

    line_ids = fields.One2many('account.exchange.document.line', 'exchange_document_id')

    date_start = fields.Date('Date Start', default=date.today())
    date_stop = fields.Date('Date Stop', default=date.today())
    amount = fields.Monetary('Amount', compute="_get_total", digits='Product Price')
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True,
                                 help="Company related to this treasury", default=lambda self: self.env.user.company_id)
    move_id = fields.Many2one('account.move', 'Account Move', readonly=True)
    move_ids = fields.One2many(related='move_id.line_ids', relation='account.move.line', string='Journal Items',
                               readonly=True)
    document_state = fields.Selection([('versed', 'Versed')], string="Document State", default="versed")
    state = fields.Selection([('draft', 'Open'), ('valid', 'Valid'), ('cancel', 'Cancelled')], 'State', required=True, readonly=True, index=1, default='draft')
    bank_commission = fields.Float('Bank Commission', digits='Product Price')
    bank_commission_total = fields.Float('Bank Commission Total', compute="_get_bank_commission_total", digits='Product Price')
    bank_commission_account = fields.Many2one('account.account', 'Bank Commission Account')
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, related='company_id.currency_id', store=True)

    date = fields.Date('Date', required=True)
    treasury_ids = fields.One2many('account.treasury', 'exchange_document_id', string='Associated Document')


    @api.onchange('bank_source_ids', 'date_start', 'date_stop')
    def onchange_journal(self):
        document_ids = False
        if len(self.bank_source_ids) == 0:
            if self.date_start and self.date_stop:
                document_ids = self.env['account.treasury'].search([('state', '=', self.document_state),
                                                                    ('maturity_date', '>=', self.date_start),
                                                                    ('maturity_date', '<=', self.date_stop),
                                                                    ('payment_type', '=', 'inbound'),
                                                                    ('company_id', '=', self.company_id.id),
                                                                    ('journal_id', '=', self.journal_id.id)])

                print('Treasury', document_ids)
        else:
            if self.date_start and self.date_stop:
                document_ids = self.env['account.treasury'].search([('state', '=', self.document_state),
                                                                    ('maturity_date', '>=', self.date_start),
                                                                    ('maturity_date', '<=', self.date_stop),
                                                                    ('payment_type', '=', 'inbound'),
                                                                    ('company_id', '=', self.company_id.id),
                                                                    ('journal_id', '=', self.journal_id.id),
                                                                    ('bank_source', 'in', self.bank_source_ids.ids)])
                # document_ids = [(0, 0, [x.id for x in inv])]

        self.treasury_ids = [Command.link(x.id) for x in document_ids]
        print('Treasury', self.treasury_ids)


    def button_validate(self):
        for document in self:
            for line in document.treasury_ids:
                if line.payment_type == 'inbound':
                    line.state = 'paid'
                if line.payment_type == 'outbound':
                    line.state = 'paid'
            document.state = 'valid'

    def button_cancel(self):
        for document in self:
            if document.treasury_ids:
                for rec in document.treasury_ids:
                    if rec.payment_type == 'inbound':
                        rec.state = 'versed'
                    if rec.payment_type == 'outbound':
                        rec.state = 'in_cash'
        return self.write({'state': 'cancel'})

    def button_draft(self):
        for document in self:
            if document.treasury_ids:
                for rec in document.treasury_ids:
                    if rec.payment_type == 'inbound':
                        rec.state = 'versed'
                    if rec.payment_type == 'outbound':
                        rec.state = 'in_cash'
        return self.write({'state': 'draft'})

    @api.depends('line_ids')
    def _get_total(self):
        total = 0.0
        for line in self.treasury_ids:
            total += line.amount
        amount_total = total
        self.amount = amount_total

    @api.depends('bank_commission', 'line_ids')
    def _get_bank_commission_total(self):
        self.bank_commission_total = len(self.treasury_ids) * self.bank_commission

