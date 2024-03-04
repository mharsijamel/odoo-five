from odoo import fields, models, api, _


class ConcernedUsers(models.Model):
    _name = 'concerned.users'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Concerned users'

    name = fields.Char('Name', default="New", readonly=True)
    user_id = fields.Many2one('res.users', 'User To Notify', tracking=True, required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        name = vals.get('Name', False)
        if not name or vals['name'] == _('New'):
            print("test")
            vals['name'] = self.env['ir.sequence'].next_by_code('concerned.users') or _('New')
        return super(ConcernedUsers, self).create(vals)

    def write(self, vals):
        name = vals.get('Name', False)
        if not name or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('concerned.users') or _('New')
        return super(ConcernedUsers, self).write(vals)
