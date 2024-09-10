
from odoo import api, fields, models

class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Vehicule",
    )
    
    @api.model
    def create(self, vals):
        analytic_account = super(AccountAnalyticAccount, self).create(vals)
        if 'vehicle_id' in vals:
            vehicle = self.env['fleet.vehicle'].browse(vals['vehicle_id'])
            if vehicle.analytic_account_id != analytic_account:
                vehicle.analytic_account_id = analytic_account
        return analytic_account

    def write(self, vals):
        res = super(AccountAnalyticAccount, self).write(vals)
        if 'vehicle_id' in vals:
            vehicle = self.env['fleet.vehicle'].browse(vals['vehicle_id'])
            if vehicle.analytic_account_id != self:
                vehicle.analytic_account_id = self
        return res