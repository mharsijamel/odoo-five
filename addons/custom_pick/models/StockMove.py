from odoo import fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'

    company_id = fields.Many2one(
        'res.company', 
        string='Entreprise', 
        change_default=True,
        required=True, 
        readonly=True, 
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get('account.withholding')
    )

    company_currency_id = fields.Many2one(
        'res.currency', 
        related='company_id.currency_id',
        string="Devise de l'entreprise",
        readonly=True
    )

    sale_price = fields.Monetary(
        string='Prix de Vente', 
        currency_field='company_currency_id', 
        compute='_compute_sale_price'
    )

    def _compute_sale_price(self):
        for move in self:
            sale_order_line = move.sale_line_id
            if sale_order_line:
                move.sale_price = sale_order_line.price_unit
            else:
                move.sale_price = 0.0
