from odoo import fields, models, api, _

class AfterSaleComplaint(models.Model):

    _name = 'after.sale.complaint'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'After Sale Complaint'



    name = fields.Char(string="Name", )

    service_id = fields.Many2one('after.sale.service', string="Service", index=True,)

    partner_id = fields.Many2one('res.partner', string="Customer",)

    user_id = fields.Many2one('res.users', string="User", required=True , default=lambda self: self.env.user)

    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

    receipt_date = fields.Date(string="Reception Date", )

    justification = fields.Text(string="Justification", )

    effective_date = fields.Date(string="Effective Date",)

    Telephone_retour = fields.Text(string="Telephone retour",)



