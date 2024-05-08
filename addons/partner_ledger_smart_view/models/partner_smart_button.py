# -*- coding: utf-8 -*-


from odoo import api, fields, models,_


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'


    def open_partner_ledger_smart_view(self):
        
    
         return {
            'type': 'ir.actions.act_window',
            'name': _('Partner Ledger'),
            'view_mode': 'tree',  # or any other view type e.g., 'tree', 'form'
            'res_model': 'account.move',  # assuming the ledger details are in 'account.move'
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
            'target': 'new',  # Opens view in a new window or inline
        }
        
