from odoo import models, fields, api, _

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def _get_user_id_from_group(self,):
        group_xml_id = 'delivered_quotation_notification.group_delivered_quotation_notification'
        group = self.env.ref(group_xml_id)
        return group.users.ids

    @api.constrains('state')
    def _check_deliverd_state(self):
        for rec in self:
            user_ids = rec._get_user_id_from_group()
            if rec.state == 'done':
                if rec.sale_id:
                    if rec.sale_id.state == 'sale':
                        for user_id in user_ids:
                            rec.activity_schedule(
                                'delivered_quotation_notification.mail_activity_sale_order',
                                note=_('Bons de commande [%s] est livré') % (rec.sale_id.name,),
                                user_id=user_id,)