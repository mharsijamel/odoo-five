from odoo import api, fields, models, _, Command
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class AccountPaymentRegister(models.TransientModel):

    _inherit = "account.payment.register"

    incash_check = fields.Boolean(string='Incash Check', compute="compute_incash_checks_treaty")

    incash_treaty = fields.Boolean(string='Incash Treaty', compute="compute_incash_checks_treaty")

    checkbook_id = fields.Many2one('account.check', string="Cheque", domain="[('state','=','available')]")

    maturity_date = fields.Date(string='Maturity Date')

    num_cheque = fields.Char(string='Cheque Number')

    num_treaty = fields.Char(string='Traite Number')


    bank_origin = fields.Many2one('res.bank', string='Bank Origin')


    @api.depends('partner_type', 'journal_id', 'payment_type', 'payment_method_line_id', 'incash_check')
    @api.onchange('partner_type', 'journal_id', 'payment_type', 'payment_method_line_id', 'incash_check')
    def compute_show_checkbook(self):
        for rec in self:
            if rec.partner_type == 'supplier' and rec.journal_id.type == 'bank' and rec.payment_type == 'outbound' and rec.payment_method_line_id.code == 'check_printing' and rec.incash_check:
                rec.show_checkbook = True
                # Apply dynamic domain to checkbook_id field based on the bank_origin
                return {
                    'domain': {
                        'checkbook_id': [('state', '=', 'available'), ('bank_id', '=', rec.bank_origin.id)]
                    }
                }
            else:
                rec.show_checkbook = False
                # If conditions don't match, clear the domain for checkbook_id
                return {
                    'domain': {
                        'checkbook_id': [('id', '=', False)]
                    }
                }


    @api.depends('journal_id',  'payment_method_line_id')
    def compute_incash_checks_treaty(self):
        for payment in self:
            _logger.info('payment.payment_method_line_id.code %s', payment.payment_method_line_id.code)
            if payment.payment_type == 'inbound' and payment.journal_id.type == 'bank':
                if payment.payment_method_line_id.code == 'check_printing':
                    payment.incash_check = True
                    _logger.info('payment.incash_check %s', payment.incash_check)
                    payment.incash_treaty = False
                elif payment.payment_method_line_id.code == 'treaty':
                    payment.incash_check = False
                    payment.incash_treaty = True
                else:
                    payment.incash_check = False
                    payment.incash_treaty = False
            elif payment.payment_type == 'outbound' and payment.journal_id.type == 'bank':
                payment.sudo().update({
                    'bank_origin': self.journal_id.bank_id.id,
                })
                if payment.payment_method_line_id.code == 'check_printing':
                    payment.incash_check = True
                    payment.incash_treaty = False
                elif payment.payment_method_line_id.code == 'treaty':
                    payment.incash_check = False
                    payment.incash_treaty = True
                else:
                    payment.incash_check = False
                    payment.incash_treaty = False
            else:
                payment.incash_check = False
                payment.incash_treaty = False

    def action_create_payments(self):
        _logger.info('test %s', self.partner_id.id)
        treasury_id = 0
        payments = self._create_payments()
        invoices = self.env['account.move'].browse(self.env.context.get('active_ids', []))
        # Access the move lines instead of account.move directly
        debit_line = payments.move_id.line_ids.filtered(lambda line: line.debit > 0)
        credit_line = payments.move_id.line_ids.filtered(lambda line: line.credit > 0)
        move_line_id = debit_line.id if self.payment_type == 'inbound' else credit_line.id
        if self.payment_type == 'inbound':
            if self.incash_check and self.payment_type == 'inbound':
                values = {
                    'name': self.num_cheque,
                    'payment_id': payments.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.payment_date,
                    'amount': self.amount,
                    'invoice_ids': [Command.link(invoices.id)],
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.bank_origin.id,
                    }
                _logger.info('Bank target for treasury %s', self.journal_id.id)
                already_exist = self.env['account.treasury'].sudo().search([('name', '=', False), ('holder', '=', self.partner_id.id), ('payment_id', '=', payments.id)])
                if already_exist:
                    already_exist.sudo().write(values)
                    check_id = already_exist
                else:
                    check_id = self.env['account.treasury'].sudo().create(values)
                treasury_id = check_id.id
            elif self.incash_treaty and self.payment_type == 'inbound':
                values = {
                    'name': self.num_treaty,
                    'payment_id': payments.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.payment_date,
                    'amount': self.amount,
                    'invoice_ids': [Command.link(invoices.id)],
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.bank_origin.id,
                }
                _logger.info('Bank target for treasuryy %s', self.journal_id.id)
                already_exist = self.env['account.treasury'].sudo().search([('name', '=', False), ('holder', '=', self.partner_id.id), ('payment_id', '=', payments.id)])
                if already_exist:
                    already_exist.sudo().write(values)
                    treaty_id = already_exist
                else:
                    treaty_id = self.env['account.treasury'].sudo().create(values)
                treasury_id = treaty_id.id
            payments.sudo().write({
                'bank_origin': self.bank_origin.id if self.incash_check or self.incash_treaty else False,
                'maturity_date': self.maturity_date if self.incash_check or self.incash_treaty else False,
                'num_cheque': self.num_cheque if self.incash_check else False,
                'num_treaty': self.num_treaty if self.incash_treaty else False,
                'treasury_id': treasury_id if treasury_id else False,
            })
            if self.maturity_date:
                for rec in payments.move_id.line_ids:
                    rec.sudo().write({
                        'date_maturity': self.maturity_date,
                    })
        elif self.payment_type == 'outbound':
            if self.journal_id.type == 'bank' and self.payment_method_line_id.code == 'check_printing':
                values = {
                    'name': str(self.checkbook_id.number).zfill(7) ,
                    'payment_id': payments.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.payment_date,
                    'amount': self.amount,
                    'invoice_ids': [Command.link(invoices.id)],
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.journal_id.bank_id.id,
                    'move_line_id': move_line_id,
                }
                already_exist = self.env['account.treasury'].sudo().search([('name', '=', '0000000'), ('holder', '=', self.partner_id.id), ('payment_id', '=', payments.id)])
                if already_exist:
                    already_exist.sudo().write(values)
                    check_id = already_exist
                else:
                    check_id = self.env['account.treasury'].sudo().create(values)
                treasury_id = check_id.id
                self.checkbook_id.compute_treasury()
                self.checkbook_id.write({'state': 'used'})

            elif self.journal_id.type == 'bank' and self.payment_method_line_id.code == 'treaty':
                values = {
                    'name': self.num_treaty,
                    'payment_id': payments.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.payment_date,
                    'amount': self.amount,
                    'invoice_ids': [Command.link(invoices.id)],
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.journal_id.bank_id.id,
                    'move_line_id': move_line_id,
                }
                already_exist = self.env['account.treasury'].sudo().search([('name', '=', False), ('holder', '=', self.partner_id.id), ('payment_id', '=', payments.id)])
                if already_exist:
                    already_exist.sudo().write(values)
                    treaty_id = already_exist
                else:
                    treaty_id = self.env['account.treasury'].sudo().create(values)
                treasury_id = treaty_id.id
            payments.sudo().write({
                'bank_origin': self.journal_id.bank_id.id if self.payment_method_line_id.code == 'check_printing' or self.payment_method_line_id.code == 'treaty' else False,
                'maturity_date': self.maturity_date if self.payment_method_line_id.code == 'check_printing' or self.payment_method_line_id.code == 'treaty'  else False,
                'num_cheque': str(self.checkbook_id.number).zfill(7) if self.payment_method_line_id.code == 'check_printing' else False,
                'num_treaty': self.num_treaty if self.payment_method_line_id.code == 'treaty' else False,
                'treasury_id': treasury_id if treasury_id else False,
                'checkbook_id': self.checkbook_id.id if self.checkbook_id else False,
            })
            if self.maturity_date:
                for rec in payments.move_id.line_ids:
                    rec.sudo().write({
                        'date_maturity': self.maturity_date,
                    })

        if self._context.get('dont_redirect_to_payments'):
            return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        
        return action
