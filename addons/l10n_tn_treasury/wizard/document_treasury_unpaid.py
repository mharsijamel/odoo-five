from odoo import fields, models, api
from odoo.exceptions import UserError


class DocumentTreasuryUnpaid(models.TransientModel):
    _name = "document.treasury.unpaid"
    _description = "Unpaid Check/Treaty Wizard"

    check_id = fields.Many2one('account.treasury', string="Numéro Chèque/traite", required=True, ondelete="cascade")

    partner_id = fields.Many2one('res.partner', string="Holder", required=True)

    currency_id = fields.Many2one('res.currency', string="Devise")

    company_id = fields.Many2one('res.company', related='check_id.company_id')

    amount = fields.Float(string='Total', digits='Product Price', required=True, )
    date = fields.Date(string='Date', required=True)

    def button_confirm(self):
        self.ensure_one()
        installment_id = False
        if self.check_id.payment_type == 'inbound':

            if self.check_id.journal_id.incash_check == True :
                installment_ids = self.env['account.installment'].search([])
                for installment in installment_ids:
                    if installment.treasury_ids:
                        if self.check_id.id in installment.treasury_ids.ids:
                            installment_id = self.env['account.installment'].browse(installment.id)
                if installment_id:
                    journal_check_id = self.env['account.journal'].sudo().search([('temporary_bank_journal', '=', True),('inpayed_check', '=', True)], limit=1)
                    if journal_check_id:
                        move_vals = {
                            'ref': self.check_id.name,
                            'journal_id': journal_check_id.id,
                            'narration': False,
                            'date': self.date,
                            'line_ids': [],
                        }

                        move_line1 = {
                            'name': "Chèque Impayé de [" + self.check_id.holder.name + "] N:" + self.check_id.name or '/',
                            'company_id': journal_check_id.company_id.id,
                            'partner_id': self.check_id.holder.id,
                            'credit': 0,
                            'debit': self.check_id.amount,
                            'account_id': journal_check_id.default_account_id.id,
                            'date': self.date,
                        }
                        move_vals['line_ids'].append([0, False, move_line1])
                        move_line2 = {
                            'name': "Chèque Impayé de [" + self.check_id.holder.name + "] N:" + self.check_id.name or '/',
                            'company_id': journal_check_id.company_id.id,
                            'partner_id': self.check_id.holder.id,
                            'credit': self.check_id.amount,
                            'debit': 0,
                            'account_id': installment_id.journal_id.default_account_id.id,
                            'date': self.date,
                        }
                        move_vals['line_ids'].append([0, False, move_line2])
                        move_id = self.env['account.move'].sudo().create(move_vals)
                        move_id.sudo().post()
                        self.check_id.sudo().write({
                            'state': 'notice',
                        })
                    else:
                        raise UserError("Veuillez configurer un journal pour les chèques impayés")

            elif self.check_id.journal_id.incash_treaty == True:
                installment_ids = self.env['account.installment.trait'].search([])
                for installment in installment_ids:
                    if installment.treasury_ids:
                        if self.check_id.id in installment.treasury_ids.ids:
                            installment_id = self.env['account.installment.trait'].browse(installment.id)
                if installment_id:
                    journal_traty_id = self.env['account.journal'].sudo().search([('temporary_bank_journal', '=', True),('inpayed_treaty', '=', True)], limit=1)
                    move_vals = {
                        'ref': self.check_id.name,
                        'journal_id': journal_traty_id.id,
                        'narration': False,
                        'date': self.date,
                        'line_ids': [],
                    }
                    if journal_traty_id:
                        move_line1 = {
                            'name': "Chèque Impayé de [" + self.check_id.holder.name + "] N:" + self.check_id.name or '/',
                            'company_id': journal_traty_id.company_id.id,
                            'partner_id': self.check_id.holder.id,
                            'credit': 0,
                            'debit': self.check_id.amount,
                            'account_id': journal_traty_id.default_account_id.id,
                            'date': self.date,
                        }
                        move_vals['line_ids'].append([0, False, move_line1])
                        move_line2 = {
                            'name': "Chèque Impayé de [" + self.check_id.holder.name + "] N:" + self.check_id.name or '/',
                            'company_id': journal_traty_id.company_id.id,
                            'partner_id': self.check_id.holder.id,
                            'credit': self.check_id.amount,
                            'debit': 0,
                            'account_id': installment_id.journal_id.default_account_id.id,
                            'date': self.date,
                        }
                        move_vals['line_ids'].append([0, False, move_line2])
                        move_id = self.env['account.move'].sudo().create(move_vals)
                        move_id.sudo().post()
                        self.check_id.sudo().write({
                            'state': 'notice',
                        })
                    else:
                        raise UserError("Veuillez configurer un journal pour les traites impayées")


