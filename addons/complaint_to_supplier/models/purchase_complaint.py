
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError



class PurchaseComplaint(models.Model):

    _name = 'purchase.complaint'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Purchase Complaint'

    name = fields.Char(string='Complaint No', required=True, copy=False, readonly=True, index=True, default=lambda self: ('New'))

    date = fields.Date(string='Date', required=True, default=fields.Date.today)

    partner_id = fields.Many2one('res.partner', string='Supplier', domain="[('is_supplier', '=', True), ('company_id', 'in', (False, company_id))]", required=True)

    product_id = fields.Many2one('product.product', string='Product', required=True)

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order refernce', required=True)

    rquested_by = fields.Many2one('res.users', string='Requested By', required=True, default=lambda self: self.env.user)

    quantity = fields.Boolean(string='Quantity')

    quality = fields.Boolean(string='Quality')

    progress = fields.Boolean(string='Progress')

    damege = fields.Boolean(string='Damage')

    other = fields.Boolean(string='Other')

    description = fields.Text(string='Complaint')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('sent', 'Sent'),
        ('closed', 'Closed'),
        ('cancel', 'Cancel'),
        ],readonly=True, tracking=True, default='draft')

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible', index=True, tracking=True, default=lambda self: self.env.user)


    def get_users_group(self):
        group = self.env['res.groups'].search([('name','=','Purchase Administrator')])
        return group.users.ids

    def button_request(self):
        self.state = 'waiting'
        user_ids = self.get_users_group()
        print(user_ids)
        if user_ids:
            self.activity_schedule(
                'complaint_to_supplier.mail_activity_complaint',
                note=_('New Request created by %s') % (self.rquested_by.name,) ,
                user_id= user_ids[0],)
        else:
            raise Warning(
                _("Vérifier avec votre administrateur si la configuration des responsable achats est bien définie !!"))

    def button_approve(self):
        self.state = 'approved'

    def button_close(self):
        self.state = 'closed'

    def button_cancel(self):
        self.state = 'cancel'


    def get_mail_template(self):
        template_id = self.env.ref('complaint_to_supplier.email_template_complaint_to_supplier')
        return template_id.id

    def button_send(self):
            self.ensure_one()
            template_id = self.get_mail_template()
            lang = self.env.context.get('lang')
            template = self.env['mail.template'].browse(template_id)
            if template.lang:
                lang = template._render_template(template.lang, 'purchase.complaint', self.ids[0])
            ctx = {
                'default_model': 'purchase.complaint',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                # 'custom_layout': "mail.mail_notification_paynow",
                'custom_layout': "complaint_to_supplier.mail_complaint_to_supplier",
                'force_email': True,
                # 'model_description': self.with_context(lang=lang).type_name,
            }
            self.state = 'sent'
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'complaint.supplier.ref') or 'New'
        result = super(PurchaseComplaint, self).create(vals)
        return result
    

