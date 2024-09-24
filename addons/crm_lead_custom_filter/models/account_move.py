from odoo import models, fields, api

class AccountMove(models.Model):

    _inherit = 'account.move'

    city = fields.Char(string='Ville', related='partner_id.city', store=True)