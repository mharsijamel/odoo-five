
from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError


class AccountTreasury(models.Model):

    _name = 'account.treasury'
    _description = 'Treasury'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string='Name', readonly=True, )

    holder = fields.Many2one('res.partner', string='Holder', required=True)

    amount = fields.Float(string='Total', digits='Product Price', required=True, readonly=True, )

    maturity_date = fields.Date(string='Maturity Date', readonly=True, )

    payment_date = fields.Date(string='Payment Date', required=True, readonly=True, )

    payment_id = fields.Many2one('account.payment', string='Payment ref', required=True, readonly=True, )
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True, )

    invoice_ids = fields.Many2many('account.move', string='Invoice ref', readonly=True, )

    user_id = fields.Many2one('res.users', string='User', required=True, readonly=True,
                              default=lambda self: self.env.user)

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)


    # document_type = fields.Many2one('account.document.type', string='Document Type', required=True, readonly=True,)

    # transasaction_type = fields.Selection([('in', 'In'), ('out', 'Out')], string='Transaction Type', required=True, readonly=True,)

    state = fields.Selection([
        ('in_cash', 'In Cash'),
        # ('valid', 'Valid'), #valide
        ('versed', 'Versed'),  # liquidé
        ('paid', 'Paid'),  # paier
        ('notice', 'Notice'),  # préavis
        ('cancel', 'Cancelled'),
    ], 'State', required=True, readonly=True, index=1, default='in_cash', track_visibility='onchange')

    bank_origin = fields.Many2one('res.bank', string='Bank Origin', readonly=True, )
    bank_target = fields.Many2one('res.bank', string='Bank Target', readonly=True, )

    payment_type = fields.Selection(string='Payment Type', related='payment_id.payment_type', store=True, index=True)

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
        return True

    def check_paid_sortant(self):
        return True

