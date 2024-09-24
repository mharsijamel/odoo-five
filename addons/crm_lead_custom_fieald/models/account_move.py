from odoo import models, fields, api

class AccountMove(models.Model):

    _inherit = 'account.move'

    installation_type = fields.Selection(
        [('connected', 'Connected to Networks'), ('pumping_project', 'Pumping Project')],
        string="Installation Type", compute='_compute_installation_type', tracking=True)

    power_level = fields.Float(string='Nb. KWC',compute='_compute_power_level')



    @api.depends('invoice_origin')
    def _compute_installation_type(self):
        for rec in self:
            sale_order = self.env['sale.order'].sudo().search([('name', '=', rec.invoice_origin)], limit=1)
            if sale_order:
                rec.installation_type = sale_order.installation_type
            else:
                rec.installation_type = False


    @api.depends('invoice_origin')
    def _compute_power_level(self):
        for rec in self:
            sale_order = self.env['sale.order'].sudo().search([('name', '=', rec.invoice_origin)], limit=1)
            if sale_order:
                rec.power_level = sale_order.power_level
            else:
                rec.power_level = 0.0
