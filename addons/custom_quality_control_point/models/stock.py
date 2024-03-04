# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    to_check_quality = fields.Boolean(string='quality', compute='_comppute_to_check_quality')

    @api.onchange('product_id')
    def _comppute_to_check_quality(self):
        for rec in self:
            for product in rec.product_id:
                point_controle = self.env["quality.point"].search(
                    [("product_ids", "=", product.id), ("picking_type_ids.code", "=", 'incoming')], limit=1)
                if point_controle:
                    rec.to_check_quality = True
                else:
                    rec.to_check_quality = False

    def get_quality_point(self):
        res = self.env["quality.point"].create({"title": self.product_id.name,
                                                    "product_ids": [(6, 0, [self.product_id.id])],
                                                    "picking_type_ids": [(6, 0, [self.picking_type_id.id])],
                                                    })
        # self.to_check_quality = True
        self.sudo()._create_quality_checks()
        self.sudo().write({
            'to_check_quality': True,
        })
        return res
