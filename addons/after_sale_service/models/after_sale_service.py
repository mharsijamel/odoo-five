from odoo import fields, models, api, _

class AfterSaleService(models.Model):

    _name = 'after.sale.service'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'After Sale Service'



    name = fields.Char(string="Name", required=True)

    partner_id = fields.Many2one('res.partner', string="Customer", required=True)

    user_id = fields.Many2one('res.users', string="User", required=True , default=lambda self: self.env.user)

    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

    tage_date = fields.Date(string="Date")

    complaint_id = fields.One2many('after.sale.complaint', 'service_id', string="Complaint", )

    satisfaction = fields.Boolean(string="Satisfaction" , default=False)

    reclamtion = fields.Boolean(string="Complaint" , default=False)

    state = fields.Selection([('draft','Draft'), ('done', 'Done')],  string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')

    from_post_installation = fields.Boolean(string="From Post Installation", default=False)

    # sale_order_id = fields.Many2one('sale.order', string="Sale Order" )

    call_date = fields.Datetime('Happy Call Date', store=True, tracking=True)
    call_description = fields.Html('Call Description', tracking=True, store=True)

    @api.onchange('satisfaction',)
    def _onchange_satisfaction(self):
        if self.satisfaction == True :
            self.reclamtion = False

    @api.onchange('reclamtion')
    def _onchange_reclamtion(self):
        if self.reclamtion == True :
            self.satisfaction = False


    def action_done(self):
        self.state = 'done'

    def action_draft(self):
        self.state = 'draft'
