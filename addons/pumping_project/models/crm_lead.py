from odoo import models, fields, api, _
from odoo.exceptions import ValidationError , UserError



class CrmLead(models.Model):

    _inherit = 'crm.lead'

    installation_type = fields.Selection(
        [('connected', 'Connected to Networks'), ('pumping_project', 'Pumping Project')], default='connected',
        string="Installation Type", store=True, tracking=True, required=True)

    authorized = fields.Boolean(string='Authorized', default=True)

    not_authorized = fields.Boolean(string='Not Authorized')

    authorized_type = fields.Selection([('anme', 'ANME'), ('apia', 'APIA')], string='Type' , default='anme', tracking=True)

    pumping_project_config_id = fields.Many2one('pumping.config', string='Pumping project Config', tracking=True)

    cin_number = fields.Char(string='CIN Number', related='partner_id.nci', tracking=True)

    authorized_sondage = fields.Binary(string='Authorized Sondage', tracking=True)

    preliminary_application = fields.Binary(string='Preliminary Application form',)

    signed_preliminary_application = fields.Boolean(string='Signed Preliminary Application form',)



    @api.onchange('authorized')
    def _onchange_authorized(self):
        if self.authorized == True:
            self.not_authorized = False

    @api.onchange('not_authorized')
    def _onchange_not_authorized(self):
        if self.not_authorized == True:
            self.authorized = False


    @api.constrains('authorized','not_authorized')
    def _check_authorized(self):
        for rec in self:
            if rec.installation_type == 'pumping_project':
                if rec.authorized == False and rec.not_authorized == False:
                    raise ValidationError(_("You must select Authorized or Not Authorized"))



    def action_sale_quotations_new(self):

        if self.sale_order_count > 0:
            raise UserError(_('There Is Already a sale Order Attached to this Opportunity'))
        elif self.quotation_count > 0:
            raise UserError(
                _('You can not attach multiple Sale Quotations to the Same Opportunity, \n Please Try to Modify the existing One'))

        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
        else:
            if self.installation_type == 'connected':
                if self.counter_id:
                    return self.action_new_quotation()
                else:
                    raise UserError(_('Vous devais sélection un numéro de compteur pour créer un nouveau devis'))
            elif self.installation_type == 'pumping_project':
                return self.action_new_quotation()




