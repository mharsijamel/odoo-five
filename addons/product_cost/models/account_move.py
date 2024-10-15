from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    charge_ids = fields.One2many('account.move.line.charge', 'move_id', string='Charges')
    cost_check = fields.Boolean(string='Etat du Coût de Revient', default=False)

    