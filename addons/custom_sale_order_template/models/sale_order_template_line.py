from odoo import models, fields, api, _

class SaleOrderTemplateLine(models.Model):

    _inherit = 'sale.order.template.line'

    price_unit = fields.Float(string='Prix', digits='Product Price', default=0.0)