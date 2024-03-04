from odoo import models, fields, api, _




class AccountPayment(models.Model):
    _inherit = "account.payment"

    checkbook_id = fields.Many2one('account.check' , string="Cheque", domain="[('state','=','available')]")

    cheque_payment_date = fields.Date(string="Cheque Payment Date")

    show_checkbook = fields.Boolean(string="Show Checkbook",  compute="compute_show_checkbook")





