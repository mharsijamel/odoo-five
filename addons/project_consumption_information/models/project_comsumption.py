from odoo import fields, models, api, _


class ProjectComsumption(models.Model):

    _name = 'project.comsumption.line'
    _description = 'Project Comsumption Line'

    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade',index=True, copy=False)
    name = fields.Text(string='Description', required=False, default="/")

    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
    product_template_id = fields.Many2one(
        'product.template', string='Product Template',
        related="product_id.product_tmpl_id", domain=[('sale_ok', '=', True)])
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',
                                  domain="[('category_id', '=', product_uom_category_id)]", ondelete="restrict")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

    company_id = fields.Many2one(  related='project_id.company_id', string='Company', store=True, index=True)

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return

        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            self.update({
                'product_uom': self.product_id.uom_id,
                'product_uom_qty': self.product_uom_qty or 1.0
            })

        product = self.product_id
        if product and product.sale_line_warn != 'no-message':
            if product.sale_line_warn == 'block':
                self.product_id = False
            return {
                'warning': {
                    'title': _("Warning for %s", product.name),
                    'message': product.sale_line_warn_msg,
                }
            }

