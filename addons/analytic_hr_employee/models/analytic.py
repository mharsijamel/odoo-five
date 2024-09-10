
from odoo import api, fields, models
from datetime import date, timedelta

class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
    )
    
    @api.model
    def create(self, vals):
        analytic_account = super(AccountAnalyticAccount, self).create(vals)
        if 'employee_id' in vals:
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            if employee.analytic_account_id != analytic_account:
                employee.analytic_account_id = analytic_account
        return analytic_account

    def write(self, vals):
        res = super(AccountAnalyticAccount, self).write(vals)
        if 'employee_id' in vals:
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            if employee.analytic_account_id != self:
                employee.analytic_account_id = self
        return res
    
    def get_current_month_balance(self):
        ResCurrency = self.env["res.currency"]
        AccountAnalyticLine = self.env["account.analytic.line"]
        user_currency_id = self.env.user.company_id.currency_id

        today = date.today()
        start_of_month = today.replace(day=1)
        end_of_month = today.replace(day=28) + timedelta(days=4)
        end_of_month = end_of_month - timedelta(days=end_of_month.day)

        domain = [
            ("account_id", "child_of", self.id),
            ("date", ">=", start_of_month),
            ("date", "<=", end_of_month),
        ]

        credit_groups = AccountAnalyticLine.read_group(
            domain=domain + [("amount", ">=", 0.0)],
            fields=["currency_id", "amount"],
            groupby=["currency_id"],
            lazy=False,
        )
        credit = sum(
            map(
                lambda x: ResCurrency.browse(x["currency_id"][0])._convert(
                    x["amount"],
                    user_currency_id,
                    self.env.user.company_id,
                    fields.Date.today(),
                ),
                credit_groups,
            )
        )

        debit_groups = AccountAnalyticLine.read_group(
            domain=domain + [("amount", "<", 0.0)],
            fields=["currency_id", "amount"],
            groupby=["currency_id"],
            lazy=False,
        )
        debit = sum(
            map(
                lambda x: ResCurrency.browse(x["currency_id"][0])._convert(
                    x["amount"],
                    user_currency_id,
                    self.env.user.company_id,
                    fields.Date.today(),
                ),
                debit_groups,
            )
        )

        return credit - abs(debit)