from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def _get_user_id_from_group(self,):
        group_xml_id = 'confirmed_quotation_notification.group_quotation_notification'
        group = self.env.ref(group_xml_id)
        return group.users.ids
    @api.constrains('state')
    def _check_state(self):
        group_users = self._get_user_id_from_group()
        for rec in self:
            if rec.state == 'sale':
                if group_users:
                    for user in group_users:
                        rec.activity_schedule(
                            'confirmed_quotation_notification.mail_activity_sale_order',
                            note=_('Le devis [%s] est validé') % (rec.name,),
                            user_id=user,)


