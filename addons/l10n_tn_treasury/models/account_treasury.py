
from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)
class AccountTreasury(models.Model):

    _name = 'account.treasury'
    _description = 'Treasury'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string='Name', readonly=True, )

    holder = fields.Many2one('res.partner', string='Holder', required=True)

    amount = fields.Float(string='Total', digits='Product Price', required=True, readonly=True, )

    maturity_date = fields.Date(string='Maturity Date', readonly=True, )
    move_line_id = fields.Many2one('account.move.line', 'Move Line', readonly=True)
    payment_date = fields.Date(string='Payment Date', required=True, readonly=True, )

    payment_id = fields.Many2one('account.payment', string='Payment ref', readonly=True,ondelete="cascade", )
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True, )

    invoice_ids = fields.Many2many('account.move', string='Invoice ref', readonly=True, )
    move_id = fields.Many2one('account.move', string='Account Move', copy=False)
    user_id = fields.Many2one('res.users', string='User', required=True, readonly=True,
                              default=lambda self: self.env.user)

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)

    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method', related='payment_id.payment_method_line_id', store=True, index=True)
    # document_type = fields.Many2one('account.document.type', string='Document Type', required=True, readonly=True,)

    # transasaction_type = fields.Selection([('in', 'In'), ('out', 'Out')], string='Transaction Type', required=True, readonly=True,)

    state = fields.Selection([
        ('in_cash', 'In Cash'),
        # ('valid', 'Valid'), #valide
        ('versed', 'Versed'),  # liquidé
        ('paid', 'Paid'),  # paier
        ('notice', 'Notice'),  # préavis
        ('cancel', 'Cancelled'),
    ],  'State', compute='_compute_state', store=True, required=True, readonly=True, index=1, track_visibility='onchange')


    @api.depends('move_line_id.reconciled')
    def _compute_state(self):
        for record in self:
            if record.move_line_id and record.move_line_id.reconciled:
                record.state = 'paid'
            elif record.move_line_id and not record.move_line_id.reconciled and record.payment_type == 'inbound':
                record.state="versed"
            elif record.move_line_id and not record.move_line_id.reconciled and record.payment_type == 'outbound':
                record.state="notice"
            else:
                record.state = 'in_cash'

    bank_origin = fields.Many2one('res.bank', string='Bank Origin', readonly=True, )
    bank_target = fields.Many2one('res.partner.bank', string='Bank Target', readonly=True, )

    payment_type = fields.Selection(string='Payment Type', related='payment_id.payment_type', store=True, index=True)

    exchange_document_id = fields.Many2one('account.exchange.document', 'Exchange Document', ondelete="set null")

    @api.onchange('payment_id.reconciled_invoice_ids')
    def onchange_payment_invoice_ids(self):
        self.ensure_one()
        for rec in self.payment_id.reconciled_invoice_ids:
            self.sudo().write({
                'invoice_ids': [Command.link(rec)],
            })

    def button_unpaid(self):
        view_id = self.env.ref('l10n_tn_treasury.document_treasury_unpaid_wizard').id
        action = {
                'name': "Impayé",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'document.treasury.unpaid',
                'view_id': view_id,
                'views': [(view_id, 'form')],
                'target': 'new',
                'context': {
                    'default_check_id': self.id,
                    'default_partner_id': self.holder.id,
                    'default_amount': self.amount,
                }
            }
        return action

    def check_paid(self):
        view_id = self.env.ref('l10n_tn_treasury.document_treasury_paid_wizard').id
        action = {
                'name': "Versé",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'document.treasury.paid',
                'view_id': view_id,
                'views': [(view_id, 'form')],
                'target': 'new',
                'context': {
                    'default_check_id': self.id,
                    'default_partner_id': self.holder.id,
                    'default_amount': self.amount,
                }
            }
        return action


    def check_paid_sortant(self):
        return self.write({
            'state': 'paid',
        })
    def unlink(self):
        _logger.info('recording 1')
        for record in self:
            if record.state in ['versed', 'paid']:
                raise UserError(_("Vous ne pouvez pas supprimer un enregistrement de trésorerie qui est à l'état « Encours » ou « Payé »."))
            # Store references before any operation
            move = record.payment_id.move_id    
            _logger.info('recording 2')
            # Handle move deletion
            if move and move.exists():
                try:
                    move.button_cancel()
                    move.with_context(force_delete=True).unlink()
                except Exception as e:
                    _logger.warning(f"Failed to delete move {move.id}: {str(e)}")
        _logger.info('recording 3')  
        return super(AccountTreasury, self).unlink()



