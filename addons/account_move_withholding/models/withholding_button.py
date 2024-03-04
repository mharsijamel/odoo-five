# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class button_rs_view(models.Model):
    _inherit = 'account.move'

    # withholding_move_id = fields.Many2many('account.withholding', compute="account_move_withholding")
    # has_withholding = fields.Boolean('Has Withholding', compute="account_move_withholding")

    # @api.depends('invoice_ids')
    # @api.onchange('invoice_ids')
    # def account_move_withholding(self):
    #     withholding_list = []
    #     for rec in self:
    #         if rec.invoice_ids:
    #             for holding in rec.invoice_ids:
    #                 if holding.withholding_id:
    #                     withholding_list.append(holding.withholding_id.id)
    #                     rec.has_withholding = True
    #                 print("WITH", withholding_list)
    #             rec.write({
    #                 'withholding_move_id': [(6, 0, withholding_list)],
    #             })
    #
    #             # rec.withholding_move_id = [(5, 0, withholding_list)]
    #         else:
    #             rec.withholding_move_id = None
    #             rec.has_withholding = False
    #     print("WITH", self.withholding_move_id)
    #     print("WITH", rec.has_withholding)

    def action_rs(self):

        vals = self.move_type
        print(vals)
        if vals == 'out_invoice':
            types = 'out_withholding'
            withholding_tax = self.env['account.withholding.tax'].search([('type_withholding', '=', 'vente'), ('name', 'ilike', '1%')], limit=1)
            print(types)
        elif vals == 'in_invoice':
            types = 'in_withholding'
            print(types)
            withholding_tax = self.env['account.withholding.tax'].search(
                [('type_withholding', '=', 'vente'), ('name', 'ilike', '1%')], limit=1)

        if types == 'out_withholding' and withholding_tax:
            res = {
                'name': ('Retenue à la Source'),
                'res_model': 'account.withholding',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('l10n_tn_ras.account_withholding_customer_view_form').id,
                'context': {
                    'default_partner_id': self.partner_id.id,
                    'default_type': types,
                    'default_journal_id': self.journal_id.id,
                    'default_account_withholding_tax_ids': withholding_tax.id
                },
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
        elif types == 'in_withholding' and withholding_tax:
            res = {
                'name': ('Retenue à la Source'),
                'res_model': 'account.withholding',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('l10n_tn_ras.account_withholding_vendor_view_form').id,
                'context': {
                    'default_partner_id': self.partner_id.id,
                    'default_type': types,
                    'default_journal_id': self.journal_id.id,
                    'default_account_withholding_tax_ids': withholding_tax.id
                },
                'target': 'new',
                'type': 'ir.actions.act_window',
                }
        else:
            raise UserError(_("Vous ne pouvez pas accéder a ce document"))
        return res