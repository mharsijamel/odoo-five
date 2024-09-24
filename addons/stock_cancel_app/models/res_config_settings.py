# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    stock_picking_type = fields.Selection([('cancel','Cancel'),('draft','Cancel and Set to Draft'),('delete','Cancel and Delete')],string='Stock Picking Opration Type', related="company_id.stock_picking_type" ,readonly=False)
    stock_picking_scrap_type = fields.Selection([('cancel','Cancel'),('draft','Cancel and Set to Draft'),('delete','Cancel and Delete')],string='Stock Picking Opration Type', related="company_id.stock_picking_scrap_type" ,readonly=False)