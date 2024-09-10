from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class HREmployee(models.Model):
    _inherit = 'hr.employee'
    
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', store=True)