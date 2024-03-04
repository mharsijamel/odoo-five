from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner'

    is_customer = fields.Boolean('Is Customer', default=False, store=True)
    is_supplier = fields.Boolean('Is Supplier', default=False, store=True)

    localization = fields.Selection([('local', 'Local'),
                                     ('foreign', 'Foreign')], string='Localization', default='local', store=True)

    @api.model
    def check_customer(self):
        result = None
        search_state = self.env.context.get('res_partner_search_mode')
        if search_state == 'customer':
            result = True
        elif search_state == 'supplier':
            result = False
        return result

    @api.model
    def check_suplier(self):
        result = None
        search_state = self.env.context.get('res_partner_search_mode')
        if search_state == 'customer':
            result = False
        elif search_state == 'supplier':
            result = True
        return result

    @api.onchange('is_customer', 'is_supplier')
    def onchange_partner_type(self):
        for partner in self:
            if partner.is_customer:
                partner.sudo().write({'customer_rank': 1})
            else:
                partner.sudo().write({'customer_rank': 0})

            if partner.is_supplier:
                partner.sudo().write({'supplier_rank': 1})
            else:
                partner.sudo().write({'supplier_rank': 0})