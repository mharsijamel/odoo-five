from odoo import fields, models, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    attachment_ids = fields.Many2many(
        'ir.attachment', 'lead_ooprtunity_attachment_rel',
        'name', 'attachment_id',
        string='Contract Attachments',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.', store=True, tracking=True)

