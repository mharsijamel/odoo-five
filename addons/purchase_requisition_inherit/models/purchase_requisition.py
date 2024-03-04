from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    vendor_ids = fields.Many2many('res.partner', string="Multi Vendors",
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")


    def create_purchase_order(self):
        if self.vendor_ids:
            for vendor in self.vendor_ids:
                purchase_order = self.env['purchase.order'].sudo().create({
                    'partner_id': vendor.id,
                    'requisition_id': self.id,
                    'picking_type_id': self.picking_type_id.id

                })
                purchase_order._onchange_requisition_id()
        else:
            raise ValidationError(
                    _('To convert this purchase agreements to an RFQ, you have to specify vendors!!!'))



