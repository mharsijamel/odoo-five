import mimetypes

from odoo import fields, models, api, _, Command
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    installation_state = fields.Selection(
        [('prospecting', 'Prospecting'), ('contractual_commitment', 'Contractual Commitment'),
         ('pre_installation', 'Pre-installation phase'), ('internal_order', 'Internal Order'), ('planning', 'Planning'),
         ('installation', 'Installation'), ('post_installation', 'Post-installation')], default='prospecting',
        string="Installation State", store=True, tracking=True)

    installation_type = fields.Selection(
        [('connected', 'Connected to Networks')], default='connected',
        string="Installation Type", store=True, tracking=True, required=True)

    attachment_contract = fields.Binary('Document', tracking=True, related='opportunity_id.attachment_contract')
    attachment_contract_fname = fields.Char('Attachment Filename', tracking=True,
                                            related='opportunity_id.attachment_contract_fname', )

    contract_signed = fields.Boolean('Contact Signed', default=False, related='opportunity_id.contract_signed',
                                     tracking=True)

    attachment_contract_id = fields.Binary('Document', tracking=True)
    attachment_contract_id_fname = fields.Char('Attachment Filename', tracking=True)

    contract_id_signed = fields.Boolean('Contact Signed', default=False, compute="onchange_attachement_contract_id",
                                        tracking=True)

    counter_id = fields.Many2one('customer.reference', domain="[('partner_id', '=', partner_id)]")

    # Commercial file
    filing_date = fields.Date('Filing Date', store=True, tracking=True)
    poip_fees = fields.Float('POIP fees', store=True, tracking=True)
    approbation_date = fields.Date('Approbation Date', store=True, tracking=True)

    poip_attachement = fields.Binary('POIP Document', tracking=True)
    poip_attachement_fname = fields.Char('Attachment Filename', tracking=True)

    discharge_attachement = fields.Binary('Discharge Document', tracking=True)
    discharge_attachement_fname = fields.Char('Attachment Filename', tracking=True)

    # Technical  file
    lead_reception_date = fields.Date('Reception Date', store=True, tracking=True)
    lead_preparation_date = fields.Date('Preparation Date', store=True, tracking=True)
    lead_filling_date = fields.Date('Filing Date', store=True, tracking=True)
    lead_approbation_date = fields.Date('Approbation Date', store=True, tracking=True)

    # Payment Information
    payment_type = fields.Selection([('with_advance', 'With Advance'), ('without_advance', 'without Advance')],
                                    string="Payment Type", related="partner_id.payment_type", store=True, tracking=True)
    advance_amount = fields.Float('Advance Amount', default=0.0, store=True, tracking=True)

    steg_credit = fields.Float('STEG Credit', tracking=True, store=True, default=0.0)
    sub_anme = fields.Float('ANME Subvention', tracking=True, store=True, default=0.0)

    def action_confirm(self):
        amount_to_pay = ((self.amount_total - self.steg_credit - self.sub_anme) * 30) / 100
        if self.payment_type == 'with_advance' and self.advance_amount < amount_to_pay:
            raise UserError(
                _('You can not confirm sales order. You must first check the customer advance payment.'))
        elif not self.counter_id and self.installation_type == 'connected':
            raise UserError(
                _('You can not confirm sales order. You must first check the customer Counter Reference.'))

        elif not self.contract_id_signed and not self.contract_signed:
            raise UserError(
                _('You can not confirm sales order. You must first check the customer contract.'))
        else:
            if self.partner_id.is_customer:
                return super(SaleOrder, self).action_confirm()
            else:
                self.partner_id.sudo().update({
                    'is_customer': True,
                    'customer_rank': 1,
                })
                return super(SaleOrder, self).action_confirm()

    @api.onchange('attachment_contract_id')
    def onchange_attachement_contract_id(self):
        for order in self:
            if order.attachment_contract_id:
                order.contract_id_signed = True
            else:
                order.contract_id_signed = False

    @api.onchange('contract_id_signed', 'contract_signed')
    def onchange_contract_id_signed_id(self):
        for order in self:
            if order.contract_signed or order.contract_id_signed:
                order.sudo().update({'installation_state': 'contractual_commitment'})

    @api.onchange('commitment_date')
    def onchange_commitment_date_id(self):
        for order in self:
            if order.commitment_date:
                order.sudo().update({'installation_state': 'planning'})

    @api.onchange('state')
    def onchange_state_signed_id(self):
        for order in self:
            if order.state == 'sale':
                order.sudo().update({'installation_state': 'pre_installation'})

    # def write(self, vals_list):
    #     mimetype = None
    #     if mimetype is None and vals_list.get('attachment_contract_id_fname', False):
    #         mimetype = mimetypes.guess_type(vals_list['attachment_contract_id_fname'])[0]
    #         print("mimetypes", mimetype)
    #         if mimetype != 'application/pdf':
    #             raise UserError('Allowed Format Pdf')
    #     return super().write(vals_list)


    @api.onchange('lead_reception_date',)
    def onchange_lead_reception_date(self):
        for order in self:
            if order.lead_reception_date:
                if order.opportunity_id:
                    order.opportunity_id.sudo().update({'lead_reception_date': order.lead_reception_date})


    @api.onchange('lead_preparation_date')
    def onchange_lead_preparation_date(self):
        for order in self:
            if order.lead_preparation_date:
                if order.opportunity_id:
                    order.opportunity_id.sudo().update({'lead_preparation_date': order.lead_preparation_date})


    @api.onchange('lead_filling_date')
    def onchange_lead_filling_date(self):
        for order in self:
            if order.lead_filling_date:
                if order.opportunity_id:
                    order.opportunity_id.sudo().update({'lead_filling_date': order.lead_filling_date})


    @api.onchange('lead_approbation_date')
    def onchange_lead_approbation_date(self):
        for order in self:
            if order.lead_approbation_date:
                if order.opportunity_id:
                    order.opportunity_id.sudo().update({'lead_approbation_date': order.lead_approbation_date})

    @api.onchange('poip_fees')
    def onchange_poip_fees(self):
        for order in self:
            if order.poip_fees:
                if order.opportunity_id:
                    order.opportunity_id.sudo().update({'poip_fees': order.poip_fees})

    @api.onchange('steg_credit')
    def onchange_steg_credit(self):
        for order in self:
            if order.steg_credit:
                if order.opportunity_id:
                    order.opportunity_id.sudo().update({'steg_credit': order.steg_credit})

    @api.onchange('sub_anme')
    def onchange_sub_anme(self):
        for order in self:
            if order.sub_anme:
                if order.opportunity_id:
                    order.opportunity_id.sudo().update({'sub_anme': order.sub_anme})

    @api.onchange('filing_date')
    def onchange_filing_date(self):
        for order in self:
            if order.filing_date:
                if order.opportunity_id:
                    order.opportunity_id.sudo().update({'filing_date': order.filing_date})

    @api.onchange('approbation_date')
    def onchange_approbation_date(self):
        for order in self:
            if order.approbation_date:
                if order.opportunity_id:
                    order.opportunity_id.sudo().update({'approbation_date': order.approbation_date})


