from odoo import models, fields, api

class ResPartner (models.Model):
    _inherit = 'res.partner'


    supplier_classification = fields.Char(compute='_get_classification', string='Classification', readonly=True, default=' ')


    def _get_classification(self):
        for partner in self:
            evaluation = self.env['purchase.supplier.evaluation'].search([('supplier_id', '=', partner.id), ('state', '=', 'done')], limit=1, order='id desc')
            if evaluation.id:
                for record in evaluation:
                    if record.classification:
                        partner.supplier_classification = str(record.classification)
                    else:
                        partner.supplier_classification = ''
            else:
                partner.supplier_classification = ''