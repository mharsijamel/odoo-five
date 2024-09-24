from odoo import models, fields, api
from datetime import date

class CrmLead(models.Model):

    _inherit = 'crm.lead'


    win_date = fields.Date(string='Win Date')


    def _get_win_stage_id(self):
        win_stage = self.env['crm.stage'].sudo().search([('is_won', '=', True),('name', 'ilike', 'Gagné')], limit=1).id
        print(win_stage)
        return win_stage


    @api.constrains('stage_id')
    def _check_win_date(self):
        for rec in self:
            win_stage = rec._get_win_stage_id()
            print(rec.stage_id.id)
            if rec.stage_id.id == win_stage:
                rec.sudo().write({'win_date': fields.Date.today()})

