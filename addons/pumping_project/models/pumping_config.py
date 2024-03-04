from odoo import models, fields, api, _


class PumpingConfig(models.Model):

    _name = 'pumping.config'
    _inherit = ['mail.thread', 'mail.activity.mixin' ,'utm.mixin']



    name = fields.Char(string='Name', required=True, tracking=True , compute='_compute_name')

    puissance = fields.Char(string='Puissance', required=True)

    nbre_pv = fields.Char(string='Nombre de PV', required=True)

    puissance_pv = fields.Char(string='Puissance PV', required=True)

    puissance_to_install = fields.Char(string='Puissance à installer', required=True)

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)




    @api.depends('puissance','nbre_pv','puissance_pv','puissance_to_install')
    def _compute_name(self):
        for rec in self:
            rec.name = str(rec.puissance) + '/' + str(rec.nbre_pv) + '/' + str(rec.puissance_pv) + '/' + str(rec.puissance_to_install)