from odoo import models, fields, api
from odoo.exceptions import except_orm


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    city = fields.Char(string='Ville', related='partner_id.city', store=True)

    partner_state = fields.Char(string='État', related='partner_id.state_id.name', store=True)

    power_level = fields.Float(string='Nb Kilos', related='opportunity_id.power_level', store=True)

    nb_kilo = fields.Float(string='Nb Kilos (KWC)', default=0.0, store=True)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_new_quotation(self):
        res = super(CrmLead, self).action_new_quotation()
        res['context']['default_nb_kilo'] = self.power_level
        return res
