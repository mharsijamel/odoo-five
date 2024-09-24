from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    contract_signed = fields.Boolean('Contact Signed', default=False, tracking=True, readonly=True,compute='onchange_attachment_contract')

    @api.onchange('attachment_contract', 'filing_date')
    @api.depends('attachment_contract', 'filing_date')
    def onchange_attachment_contract(self):
        for lead in self:
            lead.sudo().update({'contract_signed': False})

            if lead.attachment_contract:
                lead.sudo().update({'contract_signed': True})
            else:
                if lead.filing_date:
                    lead.sudo().update({'contract_signed': True})
                else:
                    lead.sudo().update({'contract_signed': False})


