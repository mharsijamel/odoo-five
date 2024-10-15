from odoo import models, fields, api
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cost_product = fields.Float(string='Coût de Revient', compute='_compute_cost_product', store=True)
    product_part = fields.Float(string='Product Part', compute='_compute_product_part')
    charge_ids = fields.One2many('account.move.line.charge', 'move_id', string='Charges')

    @api.depends('price_unit', 'move_id.currency_id', 'move_id.company_id', 'move_id.charge_ids.amount', 'product_part')
    def _compute_cost_product(self):
        for line in self:
            _logger.info(f"Computing cost product for line: {line.id}")
            if line.move_id.currency_id and line.move_id.currency_id != line.move_id.company_id.currency_id:
                # Convert price to the company's default currency
                base_cost = line.move_id.currency_id._convert(
                    line.price_unit, 
                    line.move_id.company_id.currency_id, 
                    line.move_id.company_id, 
                    line.move_id.invoice_date or fields.Date.today()
                )
            else:
                # If it's already in the default currency
                base_cost = line.price_unit
            _logger.info(f"base_cost for move {line.move_id.id}: {base_cost}")
        
            total_charges = sum(line.move_id.charge_ids.mapped('amount'))
            _logger.info(f"Total charges for line {line.id}: {total_charges}")
            # Add charges to the base cost
            line.cost_product = base_cost + (total_charges * line.product_part)

    @api.depends('price_subtotal', 'move_id.line_ids.price_subtotal')
    def _compute_product_part(self):
        for line in self:
            total_price = sum(line.move_id.line_ids.filtered(lambda l: l.product_id).mapped('price_subtotal'))
            if total_price:
                line.product_part = line.price_subtotal / total_price
            else:
                line.product_part = 0

    """ @api.model
    def preview_cost_product(self, line_data):
 
        if line_data.get('currency_id') and line_data['currency_id'] != line_data['company_currency_id']:
            # Convert price to the company's default currency
            currency = self.env['res.currency'].browse(line_data['currency_id'])
            company_currency = self.env['res.currency'].browse(line_data['company_currency_id'])
            company = self.env['res.company'].browse(line_data['company_id'])
            base_cost = currency._convert(
                line_data['price_unit'],
                company_currency,
                company,
                line_data.get('invoice_date') or fields.Date.today()
            )
        else:
            # If it's already in the default currency
            base_cost = line_data['price_unit']

        total_charges = sum(charge['amount'] for charge in line_data.get('charge_ids', []))
        product_part = line_data.get('product_part', 0)

        cost_product = base_cost + (total_charges * product_part)

        return {
            'cost_product': cost_product,
            'base_cost': base_cost,
            'total_charges': total_charges,
        } """