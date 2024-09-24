# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'
    _description = 'Convert Lead to Opportunity (not in mass)'

    action = fields.Selection([
        ('create', 'Create a new customer'),
        ('create_contact', 'Create a new contact'),
        ('exist', 'Link to an existing customer'),
        ('nothing', 'Do not link to a customer')
    ], string='Related Customer', compute='_compute_action', readonly=False, store=True, compute_sudo=False)

    @api.depends('lead_id')
    def _compute_action(self):
        for convert in self:
            if not convert.lead_id:
                convert.action = 'nothing'
            else:
                partner = convert.lead_id._find_matching_partner()
                if partner:
                    convert.action = 'exist'
                elif convert.lead_id.contact_name:
                    convert.action = 'create'
                elif convert.lead_id.contact_name:
                    convert.action = 'create_contact'
                else:
                    convert.action = 'nothing'

    def _convert_handle_partner(self, lead, action, partner_id):
        # used to propagate user_id (salesman) on created partners during conversion
        for convert in self:
            if convert.action == 'create':
                lead.with_context(default_user_id=self.user_id.id)._handle_partner_assignment(
                    force_partner_id=partner_id,
                    create_missing=(action == 'create')
                )
            else:
                lead.with_context(default_user_id=self.user_id.id)._handle_partner_assignment(
                    force_partner_id=partner_id,
                    create_missing=(action == 'create_contact')
                )
