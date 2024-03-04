from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Order'

    date_import = fields.Date('Receipt Date', tracking=True)
    date_etd = fields.Date('ETD', tracking=True, help="Estimated date of delivery")
    date_eta = fields.Date('ETA', tracking=True, help="estimated date of arrival")
    observation = fields.Html('Observations', tracking=True)
    advancement = fields.Html('Advancement', tracking=True)
    ci_number = fields.Char('CI N°', tracking=True)
    bc_number = fields.Char('N° BC', compute="get_vendor_po_number")
    mt_declaration_do = fields.Float('MT DECLARATION DO', tracking=True)
    mt_fret = fields.Float('MT FRET', tracking=True)
    reg_vendor = fields.Boolean('REG FOURNISSEUR', tracking=True)

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    partner_localization = fields.Selection(related='partner_id.localization', string="Supplier Localization", store=True)

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES,
                                 change_default=True, tracking=True,
                                 domain="[('is_supplier', '=', True), ('company_id', 'in', (False, company_id))]",
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

    @api.onchange("partner_ref")
    def get_vendor_po_number(self):
        for order in self:
            if order.partner_ref:
                order.bc_number = order.partner_ref
            else:
                order.bc_number = ""

    @api.onchange('date_import')
    @api.depends('date_import')
    def onchange_date_import(self):
        for order in self:
            date_import = order.date_import
            if date_import:
                order.write({
                    'date_planned': datetime.strptime(str(date_import), '%Y-%m-%d'),
                })

    @api.model
    def _get_date_planned(self, seller, po=False):
        """Return the datetime value to use as Schedule Date (``date_planned``) for
           PO Lines that correspond to the given product.seller_ids,
           when ordered at `date_order_str`.

           :param Model seller: used to fetch the delivery delay (if no seller
                                is provided, the delay is 0)
           :param Model po: purchase.order, necessary only if the PO line is
                            not yet attached to a PO.
           :rtype: datetime
           :return: desired Schedule Date for the PO line
        """
        date_order = po.date_order if po else self.order_id.date_order
        date_import = po.date_import if po else self.order_id.date_import
        if date_order and not date_import:
            return date_order + relativedelta(days=seller.delay if seller else 0)
        elif date_import:
            return date_import
        else:
            return datetime.today() + relativedelta(days=seller.delay if seller else 0)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.partner_localization == 'foreign' and not order.date_import:
                raise UserError(_('To confirm this order You must enter receipt Date !!!'))

        return res

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        group_name = 'Purchase Administrator'
        group = self.env['res.groups'].search([('name', '=', group_name)])
        users_ids = self.env['res.users'].sudo().search([('groups_id', 'in', group.ids)])
        for order in self:
            if 'date_import' in vals and order.state == 'purchase':
                note = _('The Import Date of this purchase order has been updated by %s to %s') % (
                    self.env.user.partner_id.name, order.date_import)
                for user in users_ids:
                    order.activity_schedule(
                        'custom_purchase_order.mail_act_purchase_order_confirmed',
                        note=note,
                        user_id=user.id)
        return res
