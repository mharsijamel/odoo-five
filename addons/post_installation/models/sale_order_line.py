from odoo import fields, models, api, _

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'


    def _timesheet_create_project_prepare_values(self):
        print('test')
        """Generate project values"""
        account = self.order_id.analytic_account_id
        if not account:
            self.order_id._create_analytic_account(prefix=self.product_id.default_code or None)
            account = self.order_id.analytic_account_id

        # create the project or duplicate one
        return {
            'name': '%s - %s' % (self.order_id.client_order_ref, self.order_id.name) if self.order_id.client_order_ref else self.order_id.name,
            'analytic_account_id': account.id,
            'partner_id': self.order_id.partner_id.id,
            'sale_line_id': self.id,
            'active': True,
            'company_id': self.company_id.id,
            'team_id': self.order_id.project_team_id.id,
        }

    # def _timesheet_create_project_prepare_values(self):
    #     """Generate project values"""
    #     values = super()._timesheet_create_project_prepare_values()
    #     values['allow_billable'] = True
    #     return values