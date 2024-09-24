from odoo import models, fields, api

class CrmLead(models.Model):

    _inherit = 'crm.lead'


    partner_vat = fields.Char( string="Numéro d'enregistrement fiscal", related='partner_id.vat', store=True)

    # customer_reference = fields.One2many('customer.reference', 'lead_id', string='Customer Reference')