from odoo import fields, models, api


class CustomerReference(models.Model):
    _name = 'customer.reference'
    _description = 'Customer Reference'

    name = fields.Char("Reference", store=True)
    partner_id = fields.Many2one('res.partner', string="Customer")

