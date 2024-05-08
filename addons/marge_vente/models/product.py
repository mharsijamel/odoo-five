from odoo import models, fields, api

class Product(models.Model):
    _inherit = 'product.template'

    @api.onchange('standard_price', 'x_margeperc')
    def onchange_x_margeperc_standard_price(self):
        for record in self:
            record.list_price = record.standard_price + (record.standard_price * record.x_margeperc / 100)
