from odoo import api, fields, models

class StockPincking(models.Model):

    _inherit = 'stock.picking'

    Vehicle_registration = fields.Char(string='Vehicle Registration')

    driver_full_name = fields.Char(string='Driver Full Name')

    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=False, help="Date at which the transfer has been processed or cancelled.")