
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCheckBook(models.Model):
    _name = 'account.check.book'
    _inherit = ['mail.thread']
    _description = 'CheckBook'
    _rec_name = 'composed_name'
    _order = 'composed_name asc'


    premier_numero = fields.Integer('Premier Chèque', required=True, group_operator=None)
    dernier_numero = fields.Integer('Dernier Chèque', required=True, group_operator=None)

    bank_id = fields.Many2one('res.bank', string='Banque', required=False)
    composed_name = fields.Char(string="Nom Composé", store=True, compute="compute_rec_name")
    state = fields.Selection(
        [('new', 'New'), ('using', 'Using'), ('used', 'Used')],
        'Statut', compute="compute_checkbook_state", tracking=True)
    emplacement = fields.Selection(
        [('dir', 'Direction'), ('fin', 'Financier'), ('compta', 'Comptabilité')],
        'Emplacement', default='dir' ,required=True, readonly=False,tracking=True)

    check_ids = fields.One2many('account.check', 'checkbook_id', string='Cheques')

    @api.depends('premier_numero', 'dernier_numero', 'bank_id')
    def compute_rec_name(self):
        for rec in self:
            if rec.premier_numero and rec.dernier_numero and rec.bank_id:
                rec.composed_name = rec.bank_id.name + ' ' + str(rec.premier_numero).zfill(7) + '-' + str(
                    rec.dernier_numero).zfill(7)
            # else:
            #     rec.composed_name = "/"
            #     raise UserError("Veuillez vérifer la banque et les numéros du premier et dernier chèques")

    @api.depends('check_ids.state')
    def compute_checkbook_state(self):
        for rec in self:
            new = all(cheque.state == 'available' for cheque in rec.check_ids)
            used = all(cheque.state not in ('available', 'reserved') for cheque in rec.check_ids)
            if new:
                rec.state = 'new'
            elif used:
                rec.state = 'used'
            else:
                rec.state = 'using'

    def to_dir(self):
        self.emplacement = 'dir'

    def to_fin(self):
        self.emplacement = 'fin'

    def to_compta(self):
        self.emplacement = 'compta'

