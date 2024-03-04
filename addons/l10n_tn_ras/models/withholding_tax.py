from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import Warning, UserError


class AccountWithholdingTax(models.Model):
    _name = 'account.withholding.tax'

    name = fields.Char(string='Nom de la taxe', required=True)

    rate = fields.Float(string='Taux %', required=True, digits='Discount')

    account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='Compte Fiscal',
                                 ondelete='restrict', required=True, readonly=False)
    refund_account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                        string='Compte Fiscal sur les Remboursements', ondelete='restrict',
                                        readonly=False, required=True)
    type_withholding = fields.Selection([
        ('vente', 'Vente'),
        ('achat', 'Achat'),
    ], 'Type taxe', required=True, select=1, default='vente', track_visibility='onchange')

    journal_id = fields.Many2one('account.journal', string='Journal', required=True)


class AccountWithholding(models.Model):
    _name = 'account.withholding'

    def _set_name(self):
        return self.env['ir.sequence'].next_by_code('account.withholding')

    def get_account_tax(self):
        for rec in self:
            rec.tax = rec.account_withholding_tax_ids.name

    name = fields.Char(string='Name', index=True)
    tax = fields.Char(compute='get_account_tax', string='Type de retenue à la source')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('done', 'Fait'),
        ('cancel', 'Annuler')
    ], string='Statut', default='draft', readonly=True)
    type = fields.Selection([
        ('out_withholding', 'Retenue du Client'),
        ('in_withholding', 'Retenue du Fournisseur')
    ], readonly=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)

    @api.model
    def _default_journal_id(self):
        return self.env['account.journal'].search([('type', '=', 'general')], limit=1)

    journal_id = fields.Many2one('account.journal', string='Journal', default=_default_journal_id, required=True)
    partner_id = fields.Many2one('res.partner', required=True)
    account_invoice_ids = fields.One2many('account.move', inverse_name='withholding_id', string='Factures')
    account_withholding_tax_ids = fields.Many2one('account.withholding.tax', string='Type de retenue', required=True)
    account_withholding_tax_type = fields.Selection([
        ('vente', 'Vente'),
        ('achat', 'Achat'),
    ], 'Type taxe', related='account_withholding_tax_ids.type_withholding',
        readonly=True, store=True
    )
    company_id = fields.Many2one(
        'res.company', string='Entreprise', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get('account.withholding')
    )
    company_currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id',
        string="Devise de l'entreprise",
        readonly=True
    )
    amount_total_rs = fields.Monetary(string='Montant Total', compute="_compute_amount_total_rs")

    def _compute_amount_total_rs(self):
        if self.withholding_advance:
            for record in self:
                lst_price = 0.0
                lst_price_rs = 0.0
                if record.account_withholding_tax_ids:
                    invoice_sum = 0.0
                    for invoice in record.account_invoice_ids:
                        if invoice.move_type == 'out_refund':
                            invoice_sum -= invoice.amount_total
                        if invoice.move_type == 'out_invoice':
                            invoice_sum += invoice.amount_total
                        if invoice.move_type == 'in_refund':
                            invoice_sum -= invoice.amount_total
                        if invoice.move_type == 'in_invoice':
                            invoice_sum += invoice.amount_total
                    lst_price += invoice_sum
                    lst_price_rs = lst_price + record.amount_advance

            self.amount_total_rs = round(lst_price_rs, 3)
        else:
            for record in self:
                lst_price = 0.0
                if record.account_withholding_tax_ids:
                    invoice_sum = 0.0
                    for invoice in record.account_invoice_ids:
                        if invoice.move_type == 'out_refund':
                            invoice_sum -= invoice.amount_total
                        if invoice.move_type == 'out_invoice':
                            invoice_sum += invoice.amount_total
                        if invoice.move_type == 'in_refund':
                            invoice_sum -= invoice.amount_total
                        if invoice.move_type == 'in_invoice':
                            invoice_sum += invoice.amount_total
                    lst_price += invoice_sum
                record.amount_total_rs = round(lst_price, 3)
                print('test', record.amount_total_rs)

    def _compute_currency_id(self):
        self.currency_id = self.journal_id.company_id.currency_id

    currency_id = fields.Many2one('res.currency', compute='_compute_currency_id')
    retenue_amount = fields.Monetary(
        string='Retenue à la source', compute='_compute_amount',
        digits='Product Price'
    )
    amount_advance = fields.Monetary(string='Montant avance', digits='Product Price')
    withholding_advance = fields.Boolean(string='Retenue sur avance', default=0)
    account_move_id = fields.Many2one('account.move')

    @api.onchange('partner_id')
    def _partner_id_onchange(self):
        for invoice in self.account_invoice_ids:
            invoice.write({'withholding_id': False})
        self.account_invoice_ids = []

    @api.onchange('partner_id')
    def _onchange_retenu_partner_id(self):
        if self.env.context.get('default_type') in ['in_withholding']:
            journal_domain = [
                ('is_retenuachat', '=', True), ]

            default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                self.journal_id = default_journal_id

        if self.env.context.get('default_type') in ['out_withholding']:
            journal_domain = [
                ('is_retenuvente', '=', True), ]

            default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                self.journal_id = default_journal_id

    def _compute_amount(self):
        for record in self:
            sum = 0.0

            for tax in record.account_withholding_tax_ids:
                invoice_sum = 0.0
                for invoice in record.account_invoice_ids:
                    if invoice.move_type == 'out_refund':
                        invoice_sum -= invoice.amount_total
                    if invoice.move_type == 'out_invoice':
                        invoice_sum += invoice.amount_total
                    if invoice.move_type == 'in_refund':
                        invoice_sum -= invoice.amount_total
                    if invoice.move_type == 'in_invoice':
                        invoice_sum += invoice.amount_total
                sum += (invoice_sum * 0.01 * tax.rate)

                if record.withholding_advance:
                    rs_sum = 0.0
                    rs_sum = sum + (record.amount_advance * 0.01 * tax.rate)
                    record.retenue_amount = round(rs_sum, 3)
                else:
                    record.retenue_amount = round(sum, 3)

    def button_validate_withholding(self):

        self.ensure_one()
        if self.amount_advance == 0.0:
            if not all(obj.account_invoice_ids for obj in self):
                raise Warning(
                    _("Vous ne pouvez pas valider: Vous devez ajouter au moins une Ligne de facture ou entrer "
                      "un Montant d'avance."))
        if self.withholding_advance:
            today = self.date
            vals = {
                'ref': self.name + " " + self.partner_id.name,
                'journal_id': self.journal_id.id,
                'narration': False,
                'date': today,
                'partner_id': self.partner_id.id,
                'line_ids': [],
            }

            partner_account_id = self.type == 'in_withholding' and self.partner_id.property_account_payable_id.id or self.partner_id.property_account_receivable_id.id
            debit = self.type == 'in_withholding' and self.retenue_amount or 0.0
            credit = self.type == 'out_withholding' and self.retenue_amount or 0.0

            partner = {'name': self.name + " " + self.partner_id.name,
                       'journal_id': self.journal_id.id,
                       'company_id': self.journal_id.company_id.id,
                       'credit': credit,
                       'debit': debit,
                       'date': today,
                       'partner_id': self.partner_id.id,
                       'account_id': partner_account_id}
            vals['line_ids'].append([0, False, partner])

            for l in self.account_withholding_tax_ids:
                invoice_sum = self.amount_total_rs

                deb = self.type == 'in_withholding' and round((invoice_sum * l.rate) / 100, 3) or 0.0

                cred = self.type == 'out_withholding' and round((invoice_sum * l.rate) / 100, 3) or 0.0

                withholding = {'name': self.name + " " + self.partner_id.name,
                               'journal_id': self.journal_id.id,
                               'company_id': self.journal_id.company_id.id,
                               'credit': deb,
                               'debit': cred,
                               'date': today,
                               'partner_id': self.partner_id.id,
                               'account_id': self.journal_id.retenue_account_id.id}
                vals['line_ids'].append([0, False, withholding])

            self.account_move_id = self.env['account.move'].create(vals)
            counterpart_aml = self.account_move_id.line_ids.filtered(
                lambda r: r.account_id.internal_type in ('payable', 'receivable'))
            for rec in self.account_invoice_ids:
                rec.action_register_payment()
                continue
            self.account_move_id.post()
            self.state = 'done'

        else:
            today = self.date
            vals = {
                'ref': self.name + " " + self.partner_id.name,
                'journal_id': self.journal_id.id,
                'narration': False,
                'date': today,
                'partner_id': self.partner_id.id,
                'line_ids': [],
            }
            # vals for move
            partner_account_id = self.type == 'in_withholding' and self.partner_id.property_account_payable_id.id or self.partner_id.property_account_receivable_id.id
            debit = self.type == 'in_withholding' and self.retenue_amount or 0.0
            credit = self.type == 'out_withholding' and self.retenue_amount or 0.0

            partner = {'name': self.name + " " + self.partner_id.name,
                       'journal_id': self.journal_id.id,
                       'company_id': self.journal_id.company_id.id,
                       'credit': credit,
                       'debit': debit,
                       'date': today,
                       'partner_id': self.partner_id.id,
                       'account_id': partner_account_id}
            vals['line_ids'].append([0, False, partner])

            for l in self.account_withholding_tax_ids:
                invoice_sum = 0.0
                for invoice in self.account_invoice_ids:
                    if invoice.move_type == 'out_refund':
                        invoice_sum -= invoice.amount_total
                    if invoice.move_type == 'out_invoice':
                        invoice_sum += invoice.amount_total
                    if invoice.move_type == 'in_refund':
                        invoice_sum -= invoice.amount_total
                    if invoice.move_type == 'in_invoice':
                        invoice_sum += invoice.amount_total
                # deb = self.type == 'in_withholding' and round((invoice_sum * l.rate) / 100, 3) or 0.0
                #
                # cred = self.type == 'out_withholding' and round((invoice_sum * l.rate) / 100, 3) or 0.0

                withholding = {'name': self.name + " " + self.partner_id.name,
                               'journal_id': self.journal_id.id,
                               'company_id': self.journal_id.company_id.id,
                               'credit': debit,
                               'debit': credit,
                               'date': today,
                               'partner_id': self.partner_id.id,
                               'account_id': self.journal_id.retenue_account_id.id}
                vals['line_ids'].append([0, False, withholding])

            self.account_move_id = self.env['account.move'].create(vals)
            counterpart_aml = self.account_move_id.line_ids.filtered(
                lambda r: r.account_id.internal_type in ('payable', 'receivable'))
            for rec in self.account_invoice_ids:
                rec.action_register_payment()
                continue
            self.account_move_id.post()
            self.state = 'done'

    # def button_reset_to_draft_withholding(self):
    #     self.account_move_id.button_draft()
    #     self.mapped('account_move_id.line_ids').filtered(lambda line: line.is_anglo_saxon_line).unlink()
    #     self.account_move_id.unlink()
    #     # self.state = 'draft'
    #
    #     self.write({'state': 'cancel'})

    def unlink(self):
        for move in self:
            if move.name != '/' and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been posted once."))
            move.account_invoice_ids.unlink()
        return super(AccountWithholding, self).unlink()

    def button_cancel(self):
        self.account_move_id.button_draft()
        self.state = 'draft'

    def button_draft(self):
        self.account_move_id.button_cancel()
        self.state = 'cancel'

    def button_account_move(self):
        return {
            'name': 'Articles de Journal',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'res_id': self.account_move_id.id,
        }

    def __modify_account_withholding_name(self, values):
        account_holding_type = values.get('account_withholding_tax_type', False)
        if not account_holding_type and values.get('account_withholding_tax_ids'):
            withholding_id = self.env['account.withholding.tax'].browse([values.get('account_withholding_tax_ids')])
            if withholding_id.exists():
                account_holding_type = withholding_id.type_withholding
        if values.get('name', 'New') == 'New':
            if account_holding_type == 'vente':
                values['name'] = self.env['ir.sequence'].next_by_code('account.withholding')
            if account_holding_type == 'achat':
                values['name'] = self.env['ir.sequence'].next_by_code('account.withholding.achat')
        return values

    @api.model
    def create(self, values):
        values = self.__modify_account_withholding_name(values)
        result = super(AccountWithholding, self).create(values)
        return result
