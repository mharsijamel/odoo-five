from odoo import models, fields, api, _

class AccountPaymentRegister(models.TransientModel):

    _inherit = "account.payment.register"


    checkbook_id = fields.Many2one('account.check', string="Cheque", domain="[('state','=','available')]")

    cheque_payment_date = fields.Date(string="Cheque Payment Date")

    show_checkbook = fields.Boolean(string="Show Checkbook", compute="compute_show_checkbook")

    @api.depends('partner_type', 'journal_id', 'payment_type')
    @api.onchange('partner_type', 'journal_id', 'payment_type')
    def compute_show_checkbook(self):
        for rec in self:
            if rec.partner_type == 'supplier' and rec.journal_id.type == 'bank' and rec.payment_type == 'outbound' and rec.payment_method_line_id.code == 'check_printing':
                rec.show_checkbook = True
            else:
                rec.show_checkbook = False


