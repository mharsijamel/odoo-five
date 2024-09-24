# Copyright 2017 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class AccountVoucherWizard(models.TransientModel):
    _name = "account.voucher.wizard"
    _description = "Account Voucher Wizard"

    order_id = fields.Many2one("sale.order", required=True)

    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 default=lambda self: self.env.company.id)

    journal_id = fields.Many2one(
        "account.journal",
        "Journal",
        required=True,
        domain=[('company_id', '=', company_id), ("type", "in", ("bank", "cash"))],
    )
    journal_currency_id = fields.Many2one(
        "res.currency",
        "Journal Currency",
        store=True,
        readonly=False,
        compute="_compute_get_journal_currency",
    )
    currency_id = fields.Many2one("res.currency", "Currency", readonly=True)
    amount_total = fields.Monetary(readonly=True)
    amount_advance = fields.Monetary(
        "Amount advanced", required=True, currency_field="journal_currency_id"
    )
    date = fields.Date(required=True, default=fields.Date.context_today)
    currency_amount = fields.Monetary(
        "Curr. amount", readonly=True, currency_field="currency_id"
    )
    payment_ref = fields.Char("Ref.")
    payment_type = fields.Selection(
        [("inbound", "Inbound"), ("outbound", "Outbound")],
        default="inbound",
        required=True,
    )
    maturity_date = fields.Date(string='Maturity Date')

    num_cheque = fields.Char(string='Cheque Number')

    num_treaty = fields.Char(string='Traite Number')

    incash_check = fields.Boolean(string='Incash Check', compute="compute_incash_checks_treaty")

    incash_treaty = fields.Boolean(string='Incash Treaty', compute="compute_incash_checks_treaty")

    bank_origin = fields.Many2one('res.bank', string='Bank Origin')

    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method',
                                             readonly=False, copy=False, store=True,
                                             compute='_compute_payment_method_line_id',
                                             domain="[('id', 'in', available_payment_method_line_ids)]", )

    available_payment_method_line_ids = fields.Many2many('account.payment.method.line',
                                                         compute='_compute_payment_method_line_fields')

    hide_payment_method_line = fields.Boolean(
        compute='_compute_payment_method_line_fields', )


    @api.depends('company_id')
    def _compute_journal_id(self):
        for wizard in self:
            wizard.journal_id = self.env['account.journal'].search([
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', wizard.company_id.id),
            ], limit=1)

    @api.depends('payment_type', 'journal_id')
    def _compute_payment_method_line_id(self):
        for wizard in self:
            available_payment_method_lines = wizard.journal_id._get_available_payment_method_lines(wizard.payment_type)

            # Select the first available one by default.
            if available_payment_method_lines:
                wizard.payment_method_line_id = available_payment_method_lines[0]._origin
            else:
                wizard.payment_method_line_id = False

    def _get_payment_method_codes_to_exclude(self):
        # can be overriden to exclude payment methods based on the payment characteristics
        self.ensure_one()
        return []

    @api.depends('payment_type', 'journal_id', 'currency_id')
    def _compute_payment_method_line_fields(self):
        for pay in self:
            pay.available_payment_method_line_ids = pay.journal_id._get_available_payment_method_lines(pay.payment_type)
            to_exclude = pay._get_payment_method_codes_to_exclude()
            if to_exclude:
                pay.available_payment_method_line_ids = pay.available_payment_method_line_ids.filtered(
                    lambda x: x.code not in to_exclude)
            if pay.payment_method_line_id.id not in pay.available_payment_method_line_ids.ids:
                # In some cases, we could be linked to a payment method line that has been unlinked from the journal.
                # In such cases, we want to show it on the payment.
                pay.hide_payment_method_line = False
            else:
                pay.hide_payment_method_line = len(
                    pay.available_payment_method_line_ids) == 1 and pay.available_payment_method_line_ids.code == 'manual'

    @api.depends('journal_id', 'payment_method_line_id')
    def compute_incash_checks_treaty(self):
        for payment in self:
            if payment.payment_type == 'inbound' and payment.journal_id.type == 'bank':
                if payment.payment_method_line_id.code == 'check_printing':
                    payment.incash_check = True
                    payment.incash_treaty = False
                elif payment.payment_method_line_id.code == 'treaty':
                    payment.incash_check = False
                    payment.incash_treaty = True
                else:
                    payment.incash_check = False
                    payment.incash_treaty = False
            elif payment.payment_type == 'outbound' and payment.journal_id.type == 'bank':
                payment.sudo().write({
                    'bank_origin': self.journal_id.bank_id.id,
                })
                if payment.payment_method_line_id.code == 'check_printing':
                    payment.incash_check = True
                    payment.incash_treaty = False
                elif payment.payment_method_line_id.code == 'treaty':
                    payment.incash_check = False
                    payment.incash_treaty = True
                else:
                    payment.incash_check = False
                    payment.incash_treaty = False
            else:
                payment.incash_check = False
                payment.incash_treaty = False

    @api.depends("journal_id")
    def _compute_get_journal_currency(self):
        for wzd in self:
            wzd.journal_currency_id = (
                    wzd.journal_id.currency_id.id
                    or wzd.journal_id.company_id.currency_id.id
            )

    @api.constrains("amount_advance")
    def check_amount(self):
        if self.amount_advance <= 0:
            raise exceptions.ValidationError(_("Amount of advance must be positive."))
        if self.env.context.get("active_id", False):
            self.onchange_date()
            if self.payment_type == "inbound":
                if (
                        float_compare(
                            self.currency_amount,
                            self.order_id.amount_residual,
                            precision_digits=2,
                        )
                        > 0
                ):
                    raise exceptions.ValidationError(
                        _(
                            "Inbound amount of advance is greater than residual amount on sale"
                        )
                    )
            else:
                paid_in_advanced = self.order_id.amount_total - self.amount_total
                if (
                        float_compare(
                            self.currency_amount,
                            paid_in_advanced,
                            precision_digits=2,
                        )
                        > 0
                ):
                    raise exceptions.ValidationError(
                        _(
                            "Outbound amount of advance is greater than the "
                            "advanced paid amount"
                        )
                    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        sale_ids = self.env.context.get("active_ids", [])
        if not sale_ids:
            return res
        sale_id = fields.first(sale_ids)
        sale = self.env["sale.order"].browse(sale_id)
        if "amount_total" in fields_list:
            res.update(
                {
                    "order_id": sale.id,
                    "amount_total": sale.amount_residual,
                    "currency_id": sale.pricelist_id.currency_id.id,
                }
            )

        return res

    @api.onchange("journal_id", "date", "amount_advance")
    def onchange_date(self):
        if self.journal_currency_id != self.currency_id:
            amount_advance = self.journal_currency_id._convert(
                self.amount_advance,
                self.currency_id,
                self.order_id.company_id,
                self.date or fields.Date.today(),
            )
        else:
            amount_advance = self.amount_advance
        self.currency_amount = amount_advance

    def _prepare_payment_vals(self, sale):
        partner_id = sale.partner_invoice_id.commercial_partner_id.id
        if self.amount_advance < 0.0:
            raise UserError(
                _(
                    "The amount to advance must always be positive. "
                    "Please use the payment type to indicate if this "
                    "is an inbound or an outbound payment."
                )
            )

        return {
            "date": self.date,
            "amount": self.amount_advance,
            "payment_type": self.payment_type,
            "partner_type": "customer",
            "ref": self.payment_ref or sale.name,
            "journal_id": self.journal_id.id,
            "currency_id": self.journal_currency_id.id,
            "partner_id": partner_id,
            "payment_method_id": self.env.ref(
                "account.account_payment_method_manual_in"
            ).id,
            "payment_method_line_id": self.payment_method_line_id.id,
            "maturity_date": self.maturity_date,
            "num_cheque": self.num_cheque,
            "num_treaty": self.num_treaty,
            "incash_check": self.incash_check,
            "incash_treaty": self.incash_treaty,
            "bank_origin": self.bank_origin.id,
        }

    def make_advance_payment(self):
        """Create customer paylines and validates the payment"""
        self.ensure_one()
        payment_obj = self.env["account.payment"]
        sale_obj = self.env["sale.order"]
        sale_ids = self.env.context.get("active_ids", [])
        if sale_ids:
            sale_id = fields.first(sale_ids)
            sale = sale_obj.browse(sale_id)
            payment_vals = self._prepare_payment_vals(sale)
            payment = payment_obj.create(payment_vals)
            sale.account_payment_ids |= payment
            payment.action_post()

        return {
            "type": "ir.actions.act_window_close",
        }
