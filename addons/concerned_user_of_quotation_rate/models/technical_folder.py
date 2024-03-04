from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TechnicalFolder(models.Model):

    _inherit = 'technical.folder'



    def get_concerned_user_id(self):
        concerned_user_list = []
        concerned_user_id = self.env['concerned.users'].sudo().search([])
        if concerned_user_id:
            for user in concerned_user_id:
                concerned_user_list.append(user.user_id.id)
        else:
            concerned_user_list = []
        return concerned_user_list

    def approve_technical_folder_dates(self):
        concerned_user_list = self.get_concerned_user_id()
        print(concerned_user_list)
        for folder in self:
            if folder.technical_order_line and folder.order_line:
                for t_line in folder.technical_order_line:
                    for line in folder.order_line:
                        if t_line.product_id.id == line.product_id.id:
                            if (t_line.product_id.detailed_type == 'product') and (line.product_id.detailed_type == 'product') and (t_line.product_uom_qty > line.product_uom_qty) :
                                if concerned_user_list:
                                    for rec in concerned_user_list:
                                        folder.order_id.activity_schedule(
                                            'concerned_user_of_quotation_rate.mail_activity_technical_folder',
                                            note=_(' product quantity is imbalance between sale order %s and technical folder %s') % (folder.order_id.name, folder.name,),
                                            user_id=rec, )

            folder.lead_approbation_date = fields.Date.today()

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