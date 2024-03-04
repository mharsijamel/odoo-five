from odoo import models, fields, api, exceptions, _
from odoo.addons.base_vat.models.res_partner import _ref_vat
import re
import logging
_logger = logging.getLogger(__name__)

_ref_vat.update({'tn':'1499150LAM000'})

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def default_get(self, default_fields):
        res = super(res_partner, self).default_get(default_fields)
        FID = self.env['account.fiscal.position'].search([('name','=','TVA avec timbre')])
        res.update(
            property_account_position_id=FID.id if FID else False)
        return res

    __check_vat_tn = re.compile(r'^[0-9]{7}[A-Z]{3}[0-9]{3}$')

    def check_vat_tn(self, vat):
        _logger.info("checking vat ")
        if self.__check_vat_tn.match(vat):
            return True

