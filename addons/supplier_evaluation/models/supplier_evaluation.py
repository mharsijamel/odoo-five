from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SupplierEvaluation(models.Model):
    _name = 'purchase.supplier.evaluation'

    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    _description = 'Supplier Evaluation'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: ('New'))

    supplier_id = fields.Many2one('res.partner', string='Supplier', required=True,
                                  domain="[('is_supplier', '=', True), ('company_id', 'in', (False, company_id))]")

    code = fields.Char(string='Supplier Code', related='supplier_id.ref')

    customer_service = fields.Integer(string='Customer Service', required=True)

    guarantee = fields.Integer(string='Guarantee', required=True)

    payment_method = fields.Integer(string='Payment Method', required=True)

    quality = fields.Integer(string='Quality', required=True)

    price = fields.Integer(string='Price', required=True)

    period = fields.Integer(string='Period', required=True)

    final_score = fields.Float(string='Final Score', compute='_compute_final_score', store=True, readonly=True)

    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancel')], default='draft',
                             string="Status", readonly=True, required=True, tracking=True, copy=False)

    classification = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')], string='Classification', compute='_compute_classification', store=True, readonly=True)

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible', index=True, tracking=True,
                              default=lambda self: self.env.user)

    @api.depends('customer_service', 'guarantee', 'payment_method', 'quality', 'price', 'period')
    @api.onchange('customer_service', 'guarantee', 'payment_method', 'quality', 'price', 'period')
    def _compute_final_score(self):
        for record in self:
            record.final_score = (
                    (record.customer_service * 0.1) + (record.guarantee * 0.1) + (record.payment_method * 0.1) + (
                    record.quality * 0.2) + (record.price * 0.2) + (record.period * 0.2))

    @api.depends('final_score')
    @api.onchange('final_score')
    def _compute_classification(self):
        for record in self:
            if record.final_score > 3:
                record.classification = 'A'
            elif record.final_score <= 3 and record.final_score >= 2.2:
                record.classification = 'B'
            elif record.final_score <= 2.2 and record.final_score > 1.3:
                record.classification = 'C'
            elif record.final_score <= 1.3 and record.final_score >= 0.9:
                record.classification = 'D'
            else:
                record.classification = ''

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', 'New') == 'New':
    #         vals['name'] = self.env['ir.sequence'].next_by_code(
    #             'purchase.supplier.evaluation.ref') or 'New'
    #     result = super(SupplierEvaluation, self).create(vals)
    #     return result

    def button_draft(self):
        for evaluation in self:
            evaluation.sudo().update({
                'state': 'draft',
            })

    def button_cancel(self):
        for evaluation in self:
            if evaluation.state == 'draft':
                evaluation.sudo().update({
                    'state': 'cancel',
                })
            else:
                raise UserError(_('You Can not Cancel a confirmed Supplier Evaluation, Reset It to draft First !!!'))
    def button_confirm(self):
        for evaluation in self:
            if evaluation.name == 'New':
                name = self.env['ir.sequence'].next_by_code(
                'purchase.supplier.evaluation.ref')
                evaluation.sudo().update({
                    'name': name,
                })
            evaluation.sudo().update({
                'state': 'done',
            })
