from odoo import models, fields, api, _


class ResPartner(models.Model):


    _inherit = 'res.partner'


    complaint_count = fields.Integer(compute='_compute_comaint_count', string='Complaints')



    def get_complaints(self):
        self.ensure_one()
        return {
            'name': _('Complaints'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.complaint',
            'domain': [('partner_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def _compute_comaint_count(self):
        for rec in self:
            rec.complaint_count = self.env['purchase.complaint'].search_count([('partner_id','=',self.id)])
