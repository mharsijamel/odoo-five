from odoo import exceptions, fields, models, api, _
from odoo.exceptions import UserError

from datetime import datetime


class TechnicalFolder(models.Model):
    _name = 'technical.folder'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Technical Folder'

    @api.model
    def _get_default_team(self):
        return self.env['technical.team']._get_default_team_id()

    name = fields.Char('Sale Order Reference', store=True, required=True)

    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True, related='order_id.partner_id')

    order_id = fields.Many2one('sale.order', 'Sale Order')

    counter_id = fields.Many2one('customer.reference',  string='Counter Reference', related='order_id.counter_id')

    order_line = fields.One2many('sale.order.line', string='Order Lines',
                                 readonly=True, related='order_id.order_line')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)

    team_id = fields.Many2one(
        'technical.team', 'Technical Sales Team',
        ondelete="set null", tracking=True,
        change_default=True, default=_get_default_team, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'), ('done', 'Done'), ('cancel', 'Cancel')], 'State', store=True, tracking=True)


    # Technical  file
    lead_reception_date = fields.Date('Reception Date', related='order_id.lead_reception_date')
    lead_preparation_date = fields.Date('Preparation Date', store=True, tracking=True)
    lead_filling_date = fields.Date('Filing Date', store=True, tracking=True)
    lead_approbation_date = fields.Date('Approbation Date', store=True, tracking=True)


    attachment_ids = fields.Many2many(
        'ir.attachment', 'technical_folder_attachment_rel',
        'name', 'attachment_id',
        string='Attachments',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.', store=True, tracking=True)

    technical_order_line = fields.One2many('technical.order.line', 'order_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                 auto_join=True)
    note = fields.Text('Note', store=True, tracking=True)

    @api.onchange('attachment_ids')
    def onchange_technical_folder_attachments(self):
        today = datetime.now()
        for folder in self:
            if len(folder.attachment_ids) != 0:
                print('Hello')
                folder.sudo().write({
                    'lead_preparation_date': today.date(),
                })

    @api.onchange('lead_preparation_date', 'lead_filling_date')
    def onchange_technical_folder_dates(self):
        for folder in self:
            if folder.lead_preparation_date:
                folder.order_id.sudo().write({
                    'lead_preparation_date': folder.lead_preparation_date,
                })
                if folder.order_id.opportunity_id:
                    folder.order_id.opportunity_id.sudo().write({
                        'lead_preparation_date': folder.lead_preparation_date,
                    })

            if folder.lead_filling_date:
                folder.order_id.sudo().write({
                    'lead_filling_date': folder.lead_filling_date,
                })
                if folder.order_id.opportunity_id:
                    folder.order_id.opportunity_id.sudo().write({
                        'lead_filling_date': folder.lead_filling_date,
                    })

    def approve_technical_folder_dates(self):
        for folder in self:
            if len(folder.attachment_ids) == 0:
                raise UserError(_('To Approve This Technical Folder, you should at least Add One Attachments'))

            if folder.lead_approbation_date:
                folder.order_id.sudo().write({
                    'lead_approbation_date': folder.lead_approbation_date,
                })
                if folder.order_id.opportunity_id:
                    folder.order_id.opportunity_id.sudo().write({
                        'lead_approbation_date': folder.lead_approbation_date,
                    })

                folder.sudo().write({
                    'state': 'done',
                })
                folder.order_id.activity_schedule(
                    'custom_crm_lead.mail_activity_sale_order_data_updated',
                    note=_('The Technical Folder Of Sale Order with Reference %s has been Approved by %s') % (folder.order_id.name, self.env.user.name,),
                    user_id=folder.order_id.team_id.user_id.id, )

    def button_cancel(self):
        for folder in self:
            if folder.state not in ['in_progress', 'draft']:
                folder.order_id.sudo().write({
                    'state': 'cancel',
                })
            else:
                raise UserError(_('You cannot Cancel a Technical Folder that is done'))

    def button_in_progress(self):
        for folder in self:
            if folder.state not in ['in_progress']:
                folder.sudo().write({
                    'state': 'in_progress',
                })
            else:
                raise UserError(_('You cannot Change a Technical Folder State that is in progress'))







    
