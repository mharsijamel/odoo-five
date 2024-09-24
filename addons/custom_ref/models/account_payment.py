from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    invoice_refs = fields.Char(
        string="Invoice References",
        compute='_compute_invoice_refs',
        store=False  # Set to True if you want to store it in the database
    )

    @api.depends('reconciled_invoice_ids', 'reconciled_bill_ids')
    def _compute_invoice_refs(self):
        for payment in self:
            invoice_refs = payment.reconciled_invoice_ids.mapped('name')
            bill_refs = payment.reconciled_bill_ids.mapped('name')
            all_refs = invoice_refs + bill_refs
            payment.invoice_refs = ', '.join(filter(None, all_refs))