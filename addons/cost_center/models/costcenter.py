# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    cost_center = fields.Boolean(string='Cost Center', default=False, help="Indicate if this analytic account is a cost center")
    @api.model
    def create(self, vals):
        # Create the analytic account first
        account = super(AccountAnalyticAccount, self).create(vals)

        if vals.get('cost_center'):
            # Create a tag for the analytic account
            tag = self.env['account.analytic.tag'].create({
                'name': vals.get('name'),
                'active_analytic_distribution': True,  # Ensure it's marked for analytic distribution
                'company_id': vals.get('company_id', self.env.company.id),  # Assign company if provided
            })

            # Create distribution record with 100% for this analytic account
            self.env['account.analytic.distribution'].create({
                'account_id': account.id,  # Use the newly created account's ID
                'percentage': 100.0,
                'tag_id': tag.id,
            })

        return account
    
    def write(self, vals):
        if 'name' in vals and vals['name']:
            # Update the associated tag's name when the analytic account's name is changed
            for account in self:
                tag = self.env['account.analytic.tag'].search([('name', '=', account.name)], limit=1)
                if tag:
                    tag.write({'name': vals['name']})

        return super(AccountAnalyticAccount, self).write(vals)

    def unlink(self):
        for account in self:
            # Find and delete the associated tag
            tag = self.env['account.analytic.tag'].search([('name', '=', account.name)], limit=1)
            if tag:
                # Find and delete distributions associated with the tag
                distributions = self.env['account.analytic.distribution'].search([('tag_id', '=', tag.id)])
                if distributions:
                    distributions.unlink()
                
                # Delete the tag itself
                tag.unlink()

        return super(AccountAnalyticAccount, self).unlink()

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # Add the cost_center field
    cost_center = fields.Boolean(related='account_id.cost_center', string='Cost Center', readonly=True)