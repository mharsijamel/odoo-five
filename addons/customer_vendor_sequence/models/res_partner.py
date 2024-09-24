# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Res partner Sequences"

    @api.model
    def create(self, vals):
        is_customer = vals.get('is_customer', False)
        is_supplier = vals.get('is_supplier', False)
        if is_customer and not is_supplier:
            vals['ref'] = self.env['ir.sequence'].next_by_code('res.customer') or ''
        elif not is_customer and is_supplier:
            vals['ref'] = self.env['ir.sequence'].next_by_code('res.vendor') or ''
        elif is_customer and is_supplier:
            customer_ref = self.env['ir.sequence'].next_by_code('res.customer') or ''
            vendor_ref = self.env['ir.sequence'].next_by_code('res.vendor') or ''
            vals['ref'] = str(customer_ref) + "/" + str(vendor_ref)
        return super(ResPartner, self).create(vals)

    @api.constrains('is_customer', 'is_supplier')
    def set_partner_sequence(self):
        for partner in self:
            is_customer = partner.is_customer
            is_supplier = partner.is_supplier
            if is_customer and not is_supplier and not partner.ref:
                partner.ref = self.env['ir.sequence'].next_by_code('res.customer')
            elif not is_customer and is_supplier and not partner.ref:
                partner.ref = self.env['ir.sequence'].next_by_code('res.vendor')
            elif is_customer and is_supplier and not partner.ref:
                customer_ref = self.env['ir.sequence'].next_by_code('res.customer')
                vendor_ref = self.env['ir.sequence'].next_by_code('res.vendor')
                partner.ref = str(customer_ref) + "/" + str(vendor_ref)
            elif is_customer and is_supplier and partner.ref and partner.ref[:3] == '401':
                customer_ref = self.env['ir.sequence'].next_by_code('res.customer')
                old_ref = partner.ref
                partner.ref = str(customer_ref) + "/" + str(old_ref)
            elif is_customer and is_supplier and partner.ref and partner.ref[:3] == '411':
                vendor_ref = self.env['ir.sequence'].next_by_code('res.vendor')
                old_ref = partner.ref
                partner.ref = str(old_ref) + "/" + str(vendor_ref)
            else:
                continue
