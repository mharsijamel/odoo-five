from odoo import models, fields, api, _

class  Lead2OpportunityPartner(models.TransientModel):

    _inherit = 'crm.lead2opportunity.partner'



    def _create_compteur_number(self, opportunity):
        for rec in self:
            for op in opportunity:
                if op.partner_id and op.prospect_reference:
                    exitent_compteur = rec.env['customer.reference'].search([('partner_id', '=', op.partner_id.id), ('name', '=', op.prospect_reference)])
                    if not exitent_compteur:
                        res = rec.env['customer.reference'].create({
                            'partner_id': op.partner_id.id,
                            'name': op.prospect_reference,
                        })
                        return res


    def action_apply(self):
        if self.name == 'merge':
            result_opportunity = self._action_merge()
        else:
            result_opportunity = self._action_convert()

        self._create_compteur_number(result_opportunity)
        return result_opportunity.redirect_lead_opportunity_view()