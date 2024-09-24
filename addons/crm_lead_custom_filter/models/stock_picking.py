from odoo import models, fields, api

class StockPicking(models.Model):

    _inherit = 'stock.picking'


    city = fields.Char(string='Ville', related='partner_id.city', store=True)

    partner_vat = fields.Char( string="Numéro d'enregistrement fiscal", related='partner_id.vat', store=True)
    # customer_reference = fields.One2many('customer.reference', 'lead_id', string='Customer Reference')
    power_level = fields.Float(string='Nb Kilos', related='sale_id.power_level', store=True)

    installation_type = fields.Selection(
        [('connected', 'Connected to Networks'), ('pumping_project', 'Pumping Project')],
        string="Installation Type", store=True, related='sale_id.installation_type')