from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Customer Modifications'

    nci = fields.Char('NCI', placeholder="eg: 01965458", store=True, tracking=True)

    payment_type = fields.Selection([('with_advance', 'With Advance'), ('without_advance', 'without Advance')], string="Payment Type", default="with_advance", store=True, tracking=True)

    customer_reference = fields.One2many('customer.reference', 'partner_id', string="Counter Reference")


