from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    maturity_date = fields.Date(string='Maturity Date')

    num_cheque = fields.Char(string='Cheque Number')

    num_treaty = fields.Char(string='Traite Number')

    incash_check = fields.Boolean(string='Incash Check', compute="compute_incash_checks_treaty")

    incash_treaty = fields.Boolean(string='Incash Treaty', compute="compute_incash_checks_treaty")

    bank_origin = fields.Many2one('res.bank', string='Bank Origin')

    treasury_id = fields.Many2one('account.treasury', string='Treasury ID',ondelete="cascade")

    #to show check numbers (already created) only for supplier outbound check payments
    @api.depends('partner_type', 'journal_id', 'payment_type', 'payment_method_line_id', 'incash_check')
    def compute_show_checkbook(self):
        for rec in self:
            if rec.partner_type == 'supplier' and rec.journal_id.type == 'bank' and rec.payment_type == 'outbound' and rec.payment_method_line_id.code == 'check_printing' and rec.incash_check:
                rec.show_checkbook = True
            else:
                rec.show_checkbook = False

    @api.depends('move_id.line_ids.matched_debit_ids', 'move_id.line_ids.matched_credit_ids')
    def _compute_stat_buttons_from_reconciliation(self):
        res = super()._compute_stat_buttons_from_reconciliation()
        treasury = self.env['account.treasury']
        check = self.env['account.check']
        for payment in self:
            if payment.reconciled_invoice_ids:
                if len(payment.reconciled_invoice_ids) == 1:
                    treasury.browse(payment.treasury_id.id).sudo().write({
                        'invoice_ids': [Command.link(payment.reconciled_invoice_ids.id)]
                    })
                else:
                    for invoices in payment.reconciled_invoice_ids:
                        treasury.browse(payment.treasury_id.id).sudo().write({
                            'invoice_ids': [Command.link(invoices.id)]
                        })
            if payment.reconciled_bill_ids:
                if len(payment.reconciled_bill_ids) == 1:
                    treasury.browse(payment.treasury_id.id).sudo().write({
                        'invoice_ids': [Command.link(payment.reconciled_bill_ids.id)]
                    })
                    if payment.checkbook_id:
                        for inv in payment.reconciled_bill_ids:
                            check.browse(payment.checkbook_id.id).sudo().write({
                                'libelle': inv.name
                            })
                else:
                    libelle = ""
                    for bill in payment.reconciled_bill_ids:
                        treasury.browse(payment.treasury_id.id).sudo().write({
                            'invoice_ids': [Command.link(bill.id)]
                        })
                        if payment.checkbook_id:

                            for bill in payment.reconciled_bill_ids:
                                check.browse(payment.checkbook_id.id).sudo().write({
                                    'libelle': libelle + ", " + bill.name
                                })
        return res
    
    #to show num_traite ou num_cheque ou ne pas les afficher
    @api.depends('journal_id', 'payment_method_line_id')
    def compute_incash_checks_treaty(self):
        for payment in self:
            if payment.payment_type == 'inbound' and payment.journal_id.type == 'bank':
                _logger.info('payment.incash_check %s', payment.incash_check)
                _logger.info('payment.incash_treaty %s', payment.incash_treaty)
                _logger.info('payment.payment_method_line_id.code %s', payment.payment_method_line_id.code)
                if payment.payment_method_line_id.code == 'check_printing':
                    
                    payment.incash_check = True
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

    def action_post(self):
        ''' draft -> posted '''
        res = super(AccountPayment, self).action_post()
        for rec in self.move_id.line_ids:
            if self.maturity_date:
                rec.sudo().write({
                    'date_maturity': self.maturity_date,
                })
        bank_move_line = self.move_id.line_ids.filtered(lambda line: line.account_id.internal_type == 'bank')
        credit_line = self.move_id.line_ids.filtered(lambda line: line.credit > 0)
        move_line_id = credit_line.id
        _logger.info('target %s', bank_move_line.id)
        if self.payment_type == 'inbound':
            if self.incash_check and not self.treasury_id:
                values = {
                    'name': self.num_cheque,
                    'payment_id': self.move_id.payment_id.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.date,
                    'amount': self.amount,
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.bank_origin.id,
                }
                check_id = self.env['account.treasury'].sudo().create(values)

                self.sudo().write({
                    'treasury_id': check_id.id,
                })

            elif self.incash_treaty and not self.treasury_id:
                values = {
                    'name': self.num_treaty,
                    'payment_id': self.move_id.payment_id.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.date,
                    'amount': self.amount,
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.bank_origin.id,
                }
                check_id = self.env['account.treasury'].sudo().create(values)

                self.sudo().write({
                    'treasury_id': check_id.id,
                })
            elif self.incash_treaty and self.treasury_id:
                values = {
                    'name': self.num_treaty,
                    'payment_id': self.move_id.payment_id.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.date,
                    'amount': self.amount,
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.bank_origin.id,
                }
                self.treasury_id.sudo().update(values)
            elif self.incash_check and self.treasury_id:
                values = {
                    'name': self.num_cheque,
                    'payment_id': self.move_id.payment_id.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.date,
                    'amount': self.amount,
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.bank_origin.id,
                }
                self.treasury_id.sudo().update(values)
        elif self.payment_type == 'outbound':

            if self.journal_id.type == 'bank' and self.payment_method_line_id.code == 'check_printing' and not self.treasury_id:
                values = {
                    'name': str(self.checkbook_id.number).zfill(7),
                    'payment_id': self.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.date,
                    'amount': self.amount,
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.journal_id.bank_id.id,
                    'move_line_id': move_line_id ,

                }
                check_id = self.env['account.treasury'].sudo().create(values)
                self.checkbook_id.compute_treasury()
                self.sudo().write({
                    'treasury_id': check_id.id,
                })
            elif self.journal_id.type == 'bank' and self.payment_method_line_id.code == 'treaty' and not self.treasury_id:
                values = {
                    'name': self.num_treaty,
                    'payment_id': self.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.date,
                    'amount': self.amount,
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.journal_id.bank_id.id,
                    'move_line_id': move_line_id ,

                }
                treaty_id = self.env['account.treasury'].sudo().create(values)

                self.sudo().write({
                    'treasury_id': treaty_id.id,
                })
            elif self.journal_id.type == 'bank' and self.payment_method_line_id.code == 'check_printing' and self.treasury_id:
                values = {
                    'name': str(self.checkbook_id.number).zfill(7),
                    'payment_id': self.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.date,
                    'amount': self.amount,
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.journal_id.bank_id.id,
                    'move_line_id': move_line_id ,
                }
                self.treasury_id.sudo().update(values)
                self.checkbook_id.compute_treasury()

            elif self.journal_id.type == 'bank' and self.payment_method_line_id.code == 'treaty' and self.treasury_id:
                values = {
                    'name': self.num_treaty,
                    'payment_id': self.id,
                    'journal_id': self.journal_id.id,
                    'maturity_date': self.maturity_date,
                    'payment_date': self.date,
                    'amount': self.amount,
                    'user_id': self.env.user.id,
                    'company_id': self.company_id.id,
                    'holder': self.partner_id.id,
                    'state': 'in_cash',
                    'bank_origin': self.journal_id.bank_id.id,
                    'move_line_id': move_line_id ,
                }
                self.treasury_id.sudo().update(values)

        return res

    def action_cancel(self):
        super(AccountPayment, self).action_cancel()
        if self.journal_id.temporary_bank_journal:
            treasury_id = self.env['account.treasury'].search([('payment_id', '=', self.id)])
            print("treasury_id", treasury_id)
            if self.treasury_id:
                if self.treasury_id.state not in ('versed', 'cancel', 'notice', 'paid'):
                    self.treasury_id.sudo().update({'state': 'cancel'})
                else:
                    raise UserError(
                        _('You cannot delete this document because treasury document is not valid or cancel!'))
                
    def unlink(self):

        for record in self:
            _logger.info('record 1')
            if record.treasury_id and record.treasury_id.state in ['versed', 'paid','cancel','notice']:
                raise UserError(_("Vous ne pouvez pas supprimer un enregistrement de trésorerie qui est à l'état « Encours » ou « Payé »."))
            move = record.move_id
            # Handle move deletion
            if move and move.exists():
                _logger.info('record 2')
                try:
                    move.button_cancel()
                    move.with_context(force_delete=True).unlink()
                except Exception as e:
                    _logger.warning(f"Failed to delete move {move.id}: {str(e)}")
                    
            _logger.info('record 3')
        #return super(AccountPayment, self).unlink()
    
    def action_draft(self):
        for record in self:
            if record.treasury_id.state not in ['cancel','notice']:
                raise UserError(_("Vous ne pouvez pas remettre en brouillon un paiement lié à un document de trésorerie, vous pouvez juste le supprimer."))
        
        # Call the parent method to handle the usual action_draft logic
        return super(AccountPayment, self).action_draft()