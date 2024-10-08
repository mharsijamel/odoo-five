import logging
from odoo import models, fields, api

# Set up logger for your module
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    ref = fields.Char(string='Reference', readonly=True, copy=False)

    @api.model
    def create(self, vals):
        _logger.info("create() method called for res.partner with values: %s", vals)
        
        # If the partner is a customer (customer_rank > 0), assign the sequence
        if 'customer_rank' in vals and vals['customer_rank'] > 0:
            if not vals.get('ref'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('res.partner.ref') or '/'
                _logger.info("Assigned sequence to partner: %s", vals['ref'])
        
        return super(ResPartner, self).create(vals)
