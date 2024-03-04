from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'


    @api.model
    def _get_default_team(self):
        return self.env['technical.team']._get_default_team_id()

    technical_folder_id = fields.Many2one('technical.folder',  string='Technical Folder', compute='prepare_technical_folder', store=True, tracking=True)
    technical_order_line = fields.One2many('technical.order.line', string='Technical Order Line', related='technical_folder_id.technical_order_line')
    folder_count = fields.Integer(string='Number of Technical Folder', compute='_compute_technical_folder_ids',
                                   groups='technical_team_sale_order.group_technical_folder_user')
    technical_team_id = fields.Many2one(
        'technical.team', 'Technical Sales Team',
        ondelete="set null", tracking=True,
        change_default=True, default=_get_default_team, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    @api.depends('technical_folder_id')
    def _compute_technical_folder_ids(self):
        for order in self:
            if order.technical_folder_id:
                technical_folder = order.technical_folder_id
                order.folder_count = len(technical_folder)
            else:
                order.folder_count = 0.0
    @api.depends('approbation_date')
    def prepare_technical_folder(self):
        for order in self:
            if not order.technical_folder_id:
                if order.approbation_date:
                    print('order.name')
                    if order.approbation_date != order.lead_approbation_date:
                        order.sudo().write({
                            'lead_reception_date': order.approbation_date,
                        })
                        if order.technical_team_id and not order.technical_folder_id:
                            values = {
                                'name': "Technical Folder For (" + order.name + " )",
                                'partner_id': order.partner_id.id,
                                'counter_id': order.counter_id.id,
                                'order_id': order.id,
                                'order_line': order.order_line.ids,
                                'state': 'in_progress',
                                'team_id': order.technical_team_id.id,
                                'lead_reception_date': order.lead_reception_date,
                                'company_id': order.company_id.id,
                            }
                            if values:
                                if not order.technical_folder_id:
                                    order.technical_folder_id = self.env['technical.folder'].sudo().create(values)
                                    order.technical_folder_id.activity_schedule(
                                        'technical_team_sale_order.mail_activity_technical_folder_creation',
                                        note=_('A new Technical Folder request has been created by %s') % (self.env.user.name,),
                                        user_id=order.technical_team_id.user_id.id)
                else:
                    folder = self.env['technical.folder'].sudo().search([('order_id', '=', order.id)], limit=1)
                    if folder:
                        order.technical_folder_id = folder.id
                    else:
                        order.technical_folder_id = False

            else:
                folder = self.env['technical.folder'].sudo().search([('order_id', '=', order.id)], limit=1)
                order.technical_folder_id = folder.id


    def action_view_technical_folder_ids(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.technical_folder_id.id)],
            'view_mode': 'kanban,form',
            'name': _('Technical Folder'),
            'res_model': 'technical.folder',
        }
        return action
