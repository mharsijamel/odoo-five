from odoo import models, api, _, fields


class account_journal(models.Model):
    _inherit = "account.journal"

    is_retenuachat = fields.Boolean('Retenue Achat', default=False)
    is_retenuvente = fields.Boolean('Retenue vente', default=False)
    retenue_account_id = fields.Many2one('account.account', 'Retenue Account')
