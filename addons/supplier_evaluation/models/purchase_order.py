from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Order'

    @api.constrains('partner_id')
    def check_partner_classification(self):
        for order in self:
            if order.partner_id.supplier_classification == 'C' or order.partner_id.supplier_classification == 'D':
                raise UserError(_("You can not create purchase order from this supplier (%s), Because it's under range "
                                  "'%s'. Please verify with your company purchase manager" % (order.partner_id.name,
                                                                                              order.partner_id.supplier_classification)))
