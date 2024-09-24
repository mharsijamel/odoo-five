import json
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_refs = fields.Char(
        string="Payment References",
        compute='_compute_payment_refs',
        store=False  # Set to True if you want to store it in the database
    )

    @api.depends('invoice_payments_widget')
    def _compute_payment_refs(self):
        for move in self:
            payment_refs_list = []

            # Check if invoice_payments_widget is a valid JSON string
            if move.invoice_payments_widget:
                try:
                    payments_data = json.loads(move.invoice_payments_widget)

                    # Ensure 'content' exists and is a list
                    if 'content' in payments_data and isinstance(payments_data['content'], list):
                        for payment in payments_data['content']:
                            if 'ref' in payment:
                                payment_refs_list.append(payment['ref'])
                except (json.JSONDecodeError, TypeError):
                    # Log error or handle if JSON parsing fails or unexpected data types are encountered
                    move.payment_refs = ''
                    continue
            else:
                move.payment_refs = ''

            # Join payment references into a string
            move.payment_refs = ', '.join(payment_refs_list) if payment_refs_list else ''
