from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    @api.onchange('account_debit')
    def _onchange_account_debit(self):
        self._compute_analytic_account_id()

    def _compute_analytic_account_id(self):
        _logger.info(
            "Onchange triggered for account_debit: %s",
            self.account_debit.id if self.account_debit else "None"
        )

        if self.account_debit:
            # Get the analytic account based on the expense account
            rec = self.env['account.analytic.default'].account_get(
                account_id=self.account_debit.id,
                user_id=self.env.uid,
                company_id=self.company_id.id
            )
            self.analytic_account_id = rec.analytic_id.id if rec else False
        else:
            self.analytic_account_id = False
