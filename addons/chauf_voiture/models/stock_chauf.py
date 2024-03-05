from odoo import fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_chaffeur = fields.Char(string='Nom du Chauffeur', store=True)
    x_voiture = fields.Char(string='Matricule Voiture', store=True)

   
