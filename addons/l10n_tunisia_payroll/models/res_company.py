from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    _name = 'res.company'

    nombre_employes = fields.Integer(string="Nombre d'employes")
    org_ss = fields.Char(string="Organisme de sécurite sociale")
    code_org_ss = fields.Char(string="Matricule - Organisme de sécurite sociale")
