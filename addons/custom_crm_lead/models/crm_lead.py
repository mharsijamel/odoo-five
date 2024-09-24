import base64

from odoo import fields, models, api, _

import mimetypes

from odoo.exceptions import UserError
from odoo.tools.mimetypes import guess_mimetype


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    installation_state = fields.Selection(
        [('prospecting', 'Prospecting'), ('contractual_commitment', 'Contractual Commitment'),
         ('pre_installation', 'Pre-installation phase'), ('internal_order', 'Internal Order'), ('planning', 'Planning'),
         ('installation', 'Installation'), ('post_installation', 'Post-installation')], default='prospecting',
        string="Installation State", store=True, tracking=True, required=True)
    installation_type = fields.Selection(
        [('connected', 'Connected to Networks')], default='connected',
        string="Installation Type", store=True, tracking=True, required=True)

    attachment_contract = fields.Binary('Document', tracking=True)
    attachment_contract_fname = fields.Char('Attachment Filename', tracking=True)

    contract_signed = fields.Boolean('Contact Signed', default=False, tracking=True)
    counter_id = fields.Many2one('customer.reference', domain="[('partner_id', '=', partner_id)]")

    # Payment Information
    payment_type = fields.Selection([('with_advance', 'With Advance'), ('without_advance', 'without Advance')],
                                    string="Payment Type", related="partner_id.payment_type", store=True, tracking=True)
    advance_amount = fields.Float('Advance Amount', default=0.0, store=True, tracking=True)

    # Commercial file
    filing_date = fields.Date('Filing Date', store=True, tracking=True)
    poip_fees = fields.Float('POIP fees', store=True, tracking=True)
    approbation_date = fields.Date('Approbation Date', store=True, tracking=True)

    poip_attachement = fields.Binary('POIP Document', tracking=True)
    poip_attachement_fname = fields.Char('Attachment Filename', tracking=True)

    steg_credit = fields.Float('STEG Credit', tracking=True, store=True, default=0.0)
    sub_anme = fields.Float('ANME Subvention', tracking=True, store=True, default=0.0)

    discharge_attachement = fields.Binary('Discharge Document', tracking=True)
    discharge_attachement_fname = fields.Char('Attachment Filename', tracking=True)

    # Technical  file
    lead_reception_date = fields.Date('Reception Date', store=True, tracking=True)
    lead_preparation_date = fields.Date('Preparation Date', store=True, tracking=True)
    lead_filling_date = fields.Date('Filing Date', store=True, tracking=True)
    lead_approbation_date = fields.Date('Approbation Date', store=True, tracking=True)


    @api.onchange('attachment_contract')
    def onchange_attachment_contract(self):
        for lead in self:
            lead.contract_signed = False

            if lead.attachment_contract:
                lead.contract_signed = True
            else:
                lead.contract_signed = False

    @api.onchange('steg_credit', 'sub_anme')
    def onchange_attachment_contract(self):
        for lead in self:
            if lead.steg_credit:
                if lead.order_ids:
                    SaleOrder = self.env['sale.order'].browse(lead.order_ids.ids[0])

                    print("Sale Order", SaleOrder.name)
                    if SaleOrder:
                        SaleOrder.sudo().update({
                            'steg_credit': lead.steg_credit,
                        })
                        # order.activity_schedule(
                        #     'custom_crm_lead.mail_activity_sale_order_data_updated',
                        #     note=_('STEG Credit Amount Has been Updated By  %s') % (self.env.user.name,),
                        #     user_id=order.team_id.user_id.id, )

            if lead.sub_anme:
                if lead.order_ids:
                    SaleOrder = self.env['sale.order'].browse(lead.order_ids.ids[0])

                    print("Sale Order", SaleOrder.name)
                    if SaleOrder:
                        SaleOrder.sudo().update({
                            'sub_anme': lead.sub_anme,
                        })
                        # SaleOrder.activity_schedule(
                        #     'custom_crm_lead.mail_activity_sale_order_data_updated',
                        #     note=_('ANME Subvention Amount Has been Updated By  %s') % (self.env.user.name,),
                        #     user_id=order.team_id.user_id.id, )

    @api.onchange('lead_approbation_date')
    def onchange_lead_approbation_date(self):
        for lead in self:
            if lead.lead_approbation_date:
                lead.sudo().update({'installation_state': 'pre_installation'})
                if lead.order_ids:
                    SaleOrder = self.env['sale.order'].browse(lead.order_ids.ids[0])
                    if not lead.poip_attachement or not lead.discharge_attachement:
                        raise UserError(
                            _('Your Commercial File missing one of those necessary Files (POIP File, Discharge File)'))
                    SaleOrder.sudo().update({
                        'installation_state': 'pre_installation',
                        'filing_date': lead.filing_date or False,
                        'poip_fees': lead.poip_fees or 0.0,
                        'approbation_date': lead.approbation_date or False,
                        'poip_attachement': base64.b64encode(lead.poip_attachement),
                        'poip_attachement_fname': lead.poip_attachement_fname or '',
                        'discharge_attachement': base64.b64encode(lead.discharge_attachement),
                        'discharge_attachement_fname': lead.discharge_attachement_fname or '',
                        'lead_reception_date': lead.lead_reception_date or False,
                        'lead_preparation_date': lead.lead_preparation_date or False,
                        'lead_filling_date': lead.lead_filling_date or False,
                        'lead_approbation_date': lead.lead_approbation_date or False,
                        'advance_amount': lead.advance_amount or 0.0,
                    })
                    # SaleOrder.activity_schedule(
                    #     'custom_crm_lead.mail_activity_sale_order_data_updated',
                    #     note=_('Installation State Has been Updated By  %s') % (self.env.user.name,),
                    #     user_id=order.team_id.user_id.id, )
                    # print('order', order.installation_state)

    @api.onchange('approbation_date')
    def onchange_approbation_date(self):
        for lead in self:
            if lead.approbation_date:
                lead.sudo().update({'installation_state': 'internal_order'})
                if lead.order_ids:
                    if not lead.poip_attachement or not lead.discharge_attachement:
                        raise UserError(
                            _('Your Commercial File missing one of those necessary Files (POIP File, Discharge File)'))
                    SaleOrder = self.env['sale.order'].browse(lead.order_ids.ids[0])
                    print('order', SaleOrder.name)
                    if not lead.lead_approbation_date:
                        SaleOrder.sudo().update({
                            'installation_state': 'internal_order',
                            'filing_date': lead.filing_date,
                            'poip_fees': lead.poip_fees,
                            'approbation_date': lead.approbation_date,
                            'poip_attachement': base64.b64encode(lead.poip_attachement),
                            'poip_attachement_fname': lead.poip_attachement_fname or '',
                            'discharge_attachement': base64.b64encode(lead.discharge_attachement),
                            'discharge_attachement_fname': lead.discharge_attachement_fname or '',
                            'lead_reception_date': lead.lead_reception_date,
                            'lead_preparation_date': lead.lead_preparation_date,
                            'lead_filling_date': lead.lead_filling_date,
                            'lead_approbation_date': lead.lead_approbation_date,
                            'advance_amount': lead.advance_amount,
                        })
                        # SaleOrder.activity_schedule(
                        #     'custom_crm_lead.mail_activity_sale_order_data_updated',
                        #     note=_('Installation State Has been Updated By  %s') % (self.env.user.name,),
                        #     user_id=order.team_id.user_id.id, )
                        # print('order', order.installation_state)

    @api.onchange('contract_signed')
    def onchange_contract_id_signed_id(self):
        for lead in self:
            if lead.contract_signed:
                if not lead.order_ids:
                    raise UserError(_('You have to create a Quotation first'))
                if lead.installation_state == 'prospecting':
                    lead.sudo().update({'installation_state': 'contractual_commitment'})

                if lead.order_ids:
                    SaleOrder = self.env['sale.order'].browse(lead.order_ids.ids[0])
                    if SaleOrder:
                        if SaleOrder.installation_state == 'prospecting':
                            SaleOrder.sudo().update({
                                'installation_state': 'contractual_commitment',
                                'filing_date': lead.filing_date,
                                'poip_fees': lead.poip_fees,
                                'approbation_date': lead.approbation_date,
                                'poip_attachement': lead.poip_attachement,
                                'poip_attachement_fname': lead.poip_attachement_fname,
                                'discharge_attachement': lead.discharge_attachement,
                                'discharge_attachement_fname': lead.discharge_attachement_fname,
                                'lead_reception_date': lead.lead_reception_date,
                                'lead_preparation_date': lead.lead_preparation_date,
                                'lead_filling_date': lead.lead_filling_date,
                                'lead_approbation_date': lead.lead_approbation_date,
                                'advance_amount': lead.advance_amount,
                            })
                        else:
                            SaleOrder.sudo().update({
                                'installation_state': SaleOrder.installation_state,
                                'filing_date': lead.filing_date,
                                'poip_fees': lead.poip_fees,
                                'approbation_date': lead.approbation_date,
                                'poip_attachement': lead.poip_attachement,
                                'poip_attachement_fname': lead.poip_attachement_fname,
                                'discharge_attachement': lead.discharge_attachement,
                                'discharge_attachement_fname': lead.discharge_attachement_fname,
                                'lead_reception_date': lead.lead_reception_date,
                                'lead_preparation_date': lead.lead_preparation_date,
                                'lead_filling_date': lead.lead_filling_date,
                                'lead_approbation_date': lead.lead_approbation_date,
                                'advance_amount': lead.advance_amount,
                            })

    def action_sale_quotations_new(self):

        if self.sale_order_count > 0:
            raise UserError(_('There Is Already a sale Order Attached to this Opportunity'))
        elif self.quotation_count > 0:
            raise UserError(
                _('You can not attach multiple Sale Quotations to the Same Opportunity, \n Please Try to Modify the existing One'))

        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
        else:
            if self.counter_id:
                return self.action_new_quotation()
            else:
                raise UserError(_('Vous devais sélection un numéro de compteur pour créer un nouveau devis'))

    def action_new_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
        action['context'] = {
            'search_default_opportunity_id': self.id,
            'default_opportunity_id': self.id,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_source_id': self.source_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_installation_state': self.installation_state,
            'default_installation_type': self.installation_type,
            'default_counter_id': self.counter_id.id or False,
            'default_filing_date': self.filing_date,
            'default_poip_fees': self.poip_fees,
            'default_approbation_date': self.approbation_date,
            'default_poip_attachement': self.poip_attachement,
            'default_poip_attachement_fname': self.poip_attachement_fname,
            'default_discharge_attachement': self.discharge_attachement,
            'default_discharge_attachement_fname': self.discharge_attachement_fname,
            'default_lead_reception_date': self.lead_reception_date,
            'default_lead_preparation_date': self.lead_preparation_date,
            'default_lead_filling_date': self.lead_filling_date,
            'default_lead_approbation_date': self.lead_approbation_date,
            'default_payment_type': self.payment_type,
            'default_advance_amount': self.advance_amount,
            'steg_credit': self.steg_credit,
            'sub_anme': self.sub_anme,
            'default_tag_ids': [(6, 0, self.tag_ids.ids)]
        }

        if self.team_id:
            action['context']['default_team_id'] = self.team_id.id,
        if self.user_id:
            action['context']['default_user_id'] = self.user_id.id

        return action

    # def write(self, vals_list):
    #     mimetype = None
    #     print("Val List", vals_list)
    #     if mimetype is None and vals_list.get('attachment_contract_fname'):
    #         mimetype = mimetypes.guess_type(vals_list['attachment_contract_fname'])[0]
    #         print("mimetypes", mimetype)
    #         if mimetype != 'application/pdf':
    #             raise UserError('Allowed Format Pdf')
    #     return super().write(vals_list)

    @api.onchange('contract_signed')
    def onchange_contract_signed(self):
        for opportunity in self:
            if opportunity.partner_id:
                if not opportunity.partner_id.is_customer:
                    opportunity.partner_id.sudo().update({
                        'is_customer': True,
                        'customer_rank': 1
                    })

    @api.onchange('lead_reception_date')
    def _onchange_lead_reception_date(self):
        for lead in self:
            if lead.order_ids:
                SaleOrder = self.env['sale.order'].browse(lead.order_ids.ids[0])
                if SaleOrder:
                    SaleOrder.sudo().update({
                        'lead_reception_date': lead.lead_reception_date,
                    })

    @api.onchange('lead_preparation_date')
    def _onchange_lead_preparation_date(self):
        print('test')
        for lead in self:
            if lead.order_ids:
                SaleOrder = self.env['sale.order'].browse(lead.order_ids.ids[0])
                if SaleOrder:
                    SaleOrder.sudo().update({
                        'lead_preparation_date': lead.lead_preparation_date,
                    })

    @api.onchange('lead_filling_date')
    def _onchange_lead_filling_date(self):
        for lead in self:
            if lead.order_ids:
                SaleOrder = self.env['sale.order'].browse(lead.order_ids.ids[0])
                if SaleOrder:
                    SaleOrder.sudo().update({
                        'lead_filling_date': lead.lead_filling_date,
                    })

    def unlink(self):
        for lead in self:
            if lead.order_ids:
                raise UserError(_('Vous ne pouvez pas supprimer une opportunité liée à une commande'))
        return super(CrmLead, self).unlink()