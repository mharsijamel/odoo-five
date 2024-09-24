from odoo import fields, models, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    power_level = fields.Float('Power', default=0.0, tracking=True)
