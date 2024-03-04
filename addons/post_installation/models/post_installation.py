from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class PostInstallation(models.Model):


    _name = 'post.installation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Post Installation'

    name = fields.Char(string="Name", required=True)

    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)

    consumption_ids = fields.One2many('post.installation.consumption', 'install_id', string='Consumption')

    deposit_date = fields.Date(string="Filing Date")

    quality_control_date = fields.Date(string="Quality Control Date")

    reception_date = fields.Date(string="Reception Date")

    sending_date = fields.Date(string="Sending Date")

    Respensable = fields.Many2one('res.users', string='Respensable',)

    state = fields.Selection([('open', 'Open'), ('closed', 'Closed')], string='Status', readonly=True, index=True, tracking=True, default='open')

    @api.model
    def _get_name(self):
        name = self.name
        project_name = name[:-22]
        return project_name

    def action_close(self):
        self.ensure_one()
        today = fields.Date.today()
        name = self._get_name()
        if self.Respensable:
            if self.consumption_ids:
                vals = {
                    'name': name + ' - ' + 'After Sale Service',
                    'user_id': self.user_id.id,
                    'company_id': self.company_id.id,
                    'partner_id': self.partner_id.id,
                    'tage_date': today,
                    'satisfaction': True,
                    'reclamtion': False,
                    'from_post_installation': True,
                }
                after_sale = self.env['after.sale.service'].sudo().create(vals)
                self.activity_schedule(
                    'post_installation.mail_activity_post_installation',
                    note=_('Post Installation closed by %s') % (self.user_id.name,),
                    user_id=self.Respensable.id, )
                self.state = 'closed'
                return after_sale
            else:
                raise ValidationError(_("Please add consumption"))
        else:
            raise ValidationError(_("Please select a responsible for post installation"))

    def action_open(self):
        self.state = 'open'
