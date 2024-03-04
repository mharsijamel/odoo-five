from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    installation_type = fields.Selection(
        [('connected', 'Connected to Networks'), ('pumping_project', 'Pumping Project')], default='connected',
        string="Installation Type", store=True, tracking=True, required=True)

    op_authorized = fields.Boolean(string='Authorized', related='opportunity_id.authorized')

    op_authorized_type = fields.Selection([('anme', 'ANME'), ('apia', 'APIA')], string='Type', related='opportunity_id.authorized_type')

    cin_number = fields.Char(string='CIN Number', related='partner_id.nci', tracking=True)

    authorized_sondage = fields.Binary(string='Authorized Sondage', tracking=True)

    preliminary_application = fields.Binary(string='Preliminary Application form')

    signed_preliminary_application = fields.Boolean(string='Signed Preliminary Application form')



    def action_confirm(self):
        res = super().action_confirm()
        if self.technical_folder_id.state != 'done' and self.op_authorized:
            raise UserError(
                _('You can not confirm sales order. You must first make sure that the technical folder is set as done.'))
        elif not self.commitment_date:
            raise UserError(
                _('You can not confirm sales order. You must first make sure that the commitment date is set.'))
        return res



