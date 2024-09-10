from odoo import fields, models, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_amount_due = fields.Float(
        string='Solde',
        compute='_compute_payment_amount_due',
    )
    total_commande = fields.Float(
        string='Total Commandes Non Facturées',
        compute='_compute_total_commande',
    )

    @api.depends('partner_id')
    def _compute_payment_amount_due(self):
        for record in self:
            if record.partner_id:
                account_move_lines = self.env['account.move.line'].search([
                    ('partner_id', '=', record.partner_id.id),
                    ('account_id.user_type_id.type', 'in', ['receivable', 'payable']),
                    ('reconciled', '=', False)
                ])
                record.payment_amount_due = sum(line.amount_residual for line in account_move_lines)
            else:
                record.payment_amount_due = 0.0

    @api.depends('partner_id')
    def _compute_total_commande(self):
        for record in self:
            if record.partner_id:
                sale_orders = self.env['sale.order'].search([
                    ('partner_id', '=', record.partner_id.id),
                    ('invoice_status', '=', 'to invoice')
                ])
                record.total_commande = sum(order.amount_total for order in sale_orders)
            else:
                record.total_commande = 0.0