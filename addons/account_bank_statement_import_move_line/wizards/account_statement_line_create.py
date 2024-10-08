from odoo import _, api, fields, models
import logging

# Define the logger
_logger = logging.getLogger(__name__)

class AccountStatementLineCreate(models.TransientModel):
    _name = "account.statement.line.create"
    _description = "Wizard to create statement lines"

    statement_id = fields.Many2one("account.bank.statement", string="Bank Statement")
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner Related",
        domain=["|", ("parent_id", "=", False), ("is_company", "=", True)],
    )
    journal_ids = fields.Many2many("account.journal", string="Journals Filter")
    target_move = fields.Selection(
        [("posted", "All Posted Entries"), ("all", "All Entries")],
        string="Target Moves",
    )
    allow_blocked = fields.Boolean(string="Allow Litigation Move Lines")
    invoice = fields.Boolean(string="Linked to an Invoice or Refund")
    date_type = fields.Selection(
        [("due", "Due Date"), ("move", "Move Date")],
        string="Type of Date Filter",
        required=True,
    )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    debit=fields.Monetary(string="Débit", currency_field='currency_id')
    credit=fields.Monetary(string="Crédit", currency_field='currency_id')
    document = fields.Char(string="N° Pièce")
    due_date = fields.Date(default=fields.Date.context_today)
    move_date = fields.Date(default=fields.Date.context_today)
    move_line_ids = fields.Many2many("account.move.line", string="Move Lines")

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        active_model = self.env.context.get("active_model")
        if active_model == "account.bank.statement":
            statement = (
                self.env[active_model]
                .browse(self.env.context.get("active_id"))
                .exists()
            )
            if statement:
                res.update(
                    {
                        "target_move": "posted",
                        "date_type": "due",
                        "invoice": False,
                        "statement_id": statement.id,
                        "journal_ids": [(6, 0, [statement.journal_id.id])],                     }
                )
        return res

    def _prepare_move_line_domain(self):
        self.ensure_one()
        domain = [
            ("reconciled", "=", False),
            ("company_id", "=", self.env.company.id),
        ]
        if self.journal_ids:
            domain += [
                    ("journal_id", "in", self.journal_ids.ids)]
            suspense_account_ids = self.journal_ids.mapped('suspense_account_id.id')
            if suspense_account_ids:
                domain += [("account_id", "in", suspense_account_ids)]
            
        else:
            journals = self.env["account.journal"].search([])
            domain += [("journal_id", "in", journals.ids)]
            suspense_account_ids = journals.mapped('suspense_account_id.id')
            if suspense_account_ids:
                domain += [("account_id", "in", suspense_account_ids)]
        if self.partner_id:
            domain += [("partner_id", "=", self.partner_id.id)]
        if self.target_move == "posted":
            domain += [("move_id.state", "=", "posted")]
        if not self.allow_blocked:
            domain += [("blocked", "!=", True)]
        if self.date_type == "due":
            domain += [
                "|",
                ("date_maturity", "<=", self.due_date),
                ("date_maturity", "=", False),
            ]
        elif self.date_type == "move":
            domain.append(("date", "<=", self.move_date))
        if self.invoice:
            domain.append(("move_id", "!=", False))
        if self.document:
            domain.append(("ref", "ilike", self.document))
        
        if self.debit:
            domain.append(("debit", "=", self.debit))
        if self.credit:
            domain.append(("credit", "=", self.credit))
        paylines = self.env["account.payment"].search(
            [
                ("state", "in", ("draft", "posted", "sent")),
                ("line_ids", "!=", False),
            ]
        )
        #if paylines:
         #   move_in_payment_ids = paylines.mapped("line_ids.id")
        #    domain += [("id", "not in", move_in_payment_ids)]
        return domain

    def populate(self):
        domain = self._prepare_move_line_domain()
        lines = self.env["account.move.line"].search(domain)
        self.move_line_ids = False
        self.move_line_ids = lines
        action = {
            "name": _("Select Move Lines to Create Statement"),
            "type": "ir.actions.act_window",
            "res_model": "account.statement.line.create",
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
            "context": self._context,
        }
        return action

    @api.onchange(
        "date_type",
        "move_date",
        "due_date",
        "journal_ids",
        "invoice",
        "target_move",
        "allow_blocked",
        "partner_id",
        "document",
        "debit",
        "credit",
    )
    def move_line_filters_change(self):
        domain = self._prepare_move_line_domain()
        lines = self.env["account.move.line"].search(domain)
        self.move_line_ids = False
        self.move_line_ids = lines
        

    def create_statement_lines(self):
        for rec in self:
            if rec.move_line_ids and rec.statement_id:
                rec.move_line_ids.create_statement_line_from_move_line(rec.statement_id)
        return True
