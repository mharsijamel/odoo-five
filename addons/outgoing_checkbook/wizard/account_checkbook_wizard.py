# -*- coding: utf-8 -*-
# (C) 2018 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCheckbookWizard(models.TransientModel):
    _name = 'account.checkbook.wizard'
    _description = 'Account Checkbook Wizard'


    bank_id = fields.Many2one('res.bank', string='Banque', required=True)
    # company_id = fields.Many2one('res.company', 'Company', required=True)
    from_number = fields.Integer('Du Numèro')
    to_number = fields.Integer('Au Numèro')
    quantity = fields.Integer('Quantité')

    @api.onchange('from_number', 'quantity')
    def onchange_range_of_numbers(self):
        if self.quantity:
            self.to_number = self.from_number + self.quantity - 1

    @api.onchange('to_number')
    def onchange_to_number(self):
        if self.to_number:
            self.quantity = self.to_number - self.from_number + 1

    # @api.onchange('partner_id')
    # def onchange_partner(self):
    #     if self.partner_id:
    #         self.company_id = self.partner_id.company_id


    def generate_checks(self):
        self.ensure_one()
        AccountCheck = self.env['account.check']
        if not (self.from_number and self.to_number):
            raise UserError(
                _("Please define a range of numbers before generating checks"))
        if self.from_number > self.to_number:
            raise UserError(
                _("Minimal number is greather than maximum number. "
                    "Please check range of numbers."))
        if not self.from_number + self.quantity - 1 == self.to_number:
            raise UserError(
                _("Quantity seems inconsistent with range of numbers"))
        #créer le carnet de chèques
        check_book_vals = {
            'bank_id': self.bank_id.id,
            'premier_numero': self.from_number,
            'dernier_numero': self.to_number,
                           }
        check_book_id = self.env['account.check.book'].create(check_book_vals)
        common_vals = {
            'bank_id': self.bank_id.id,
            'checkbook_id': check_book_id.id,
            'state': 'available',
        }
        for number in range(self.from_number, self.to_number + 1):
            vals = dict(common_vals, number=number)
            AccountCheck.create(vals)
        # Refresh check tree view
        action = self.env.ref('outgoing_checkbook.action_account_checkbook')
        return {
            'name': _(action.name),
            'type': action.type,
            'res_model': action.res_model,
            'view_mode': action.view_mode,
            'target': 'current',
        }
