from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    signature = fields.Binary(string="Signature")
