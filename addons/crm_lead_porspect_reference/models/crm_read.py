from odoo import models, fields, api, _


class CrmLead(models.Model):

    _inherit = 'crm.lead'

    prospect_reference = fields.Char(string='Référence Porspect')




