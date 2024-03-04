from odoo import models, fields, api, _



class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    complaint_count = fields.Integer(related='partner_id.complaint_count', string='Complaints')
