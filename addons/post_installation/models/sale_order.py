from odoo import fields, models, api, _


class SaleOrder(models.Model):


    _inherit = 'sale.order'


    post_installation_id = fields.Many2one( string='Post Installation', related='project_ids.post_installation_id')

    project_team_id = fields.Many2one( 'crm.team', string='Project Team', domain="[('type_team','=','project')]", )

    project_team_visibility = fields.Boolean( string='Project Team Visibility', compute='_compute_project_team_visibility')



    # def _timesheet_create_project_prepare_values(self):
    #     print('test')
    #     """Generate project values"""
    #     account = self.order_id.analytic_account_id
    #     if not account:
    #         self.order_id._create_analytic_account(prefix=self.product_id.default_code or None)
    #         account = self.order_id.analytic_account_id
    #
    #     # create the project or duplicate one
    #     return {
    #         'name': '%s - %s' % (self.order_id.client_order_ref, self.order_id.name) if self.order_id.client_order_ref else self.order_id.name,
    #         'analytic_account_id': account.id,
    #         'partner_id': self.order_id.partner_id.id,
    #         'sale_line_id': self.id,
    #         'active': True,
    #         'company_id': self.company_id.id,
    #         'team_id': self.project_team_id.id,
    #     }

    @api.depends('order_line')
    @api.onchange('order_line')
    def _compute_project_team_visibility(self):
        service_product = 0
        for order in self:
            if order.order_line:
                for line in order.order_line:
                    if line.product_id.service_tracking == 'task_in_project' and line.product_id.project_template_id:
                        service_product += 1
                    else:
                        service_product += 0
            else:
                service_product += 0
        if service_product > 0:
            self.project_team_visibility = True
        else:
            self.project_team_visibility = False



