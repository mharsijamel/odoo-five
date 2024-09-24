# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_picking_type = fields.Selection([('cancel','Cancel'),('draft','Cancel and Set to Draft'),('delete','Cancel and Delete')],string='Stock Picking Type')
    stock_picking_scrap_type = fields.Selection([('cancel','Cancel'),('draft','Cancel and Set to Draft'),('delete','Cancel and Delete')],string='Stock Picking Scrap Type')