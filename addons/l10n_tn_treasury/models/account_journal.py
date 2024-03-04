
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['treaty'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        return res



class AccountJournal(models.Model):

    _inherit = 'account.journal'


    def _default_outbound_payment_methods(self):
        res = super()._default_outbound_payment_methods()
        res |= self.env.ref('l10n_tn_treasury.account_payment_method_treaty')
        return res

    temporary_bank_journal = fields.Boolean('Temporary Bank Journal')

    withdrawal_account = fields.Many2one( 'account.account', 'Withdrawal Account', domain="[('deprecated', '=', False), ('company_id', '=', company_id), '|', ('user_type_id', '=', default_account_type), ('user_type_id', 'in', type_control_ids), ('user_type_id.type', 'not in', ('receivable', 'payable'))]")



















