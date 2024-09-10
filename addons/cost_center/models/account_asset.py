from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    @api.onchange('account_depreciation_expense_id')
    def _onchange_account_depreciation_expense_id(self):
        self._compute_account_analytic_id()

    def _compute_account_analytic_id(self):
        _logger.info(
            "Onchange triggered for account_depreciation_expense_id: %s",
            self.account_depreciation_expense_id.id if self.account_depreciation_expense_id else "None"
        )

        if self.account_depreciation_expense_id:
            # Get the analytic account based on the expense account
            rec = self.env['account.analytic.default'].account_get(
                account_id=self.account_depreciation_expense_id.id,
                user_id=self.env.uid,
                company_id=self.company_id.id
            )
            self.account_analytic_id = rec.analytic_id.id if rec else False
        else:
            self.account_analytic_id = False
