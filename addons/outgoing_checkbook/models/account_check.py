from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCheck(models.Model):
    _name = 'account.check'
    _inherit = ['mail.thread']
    _description = 'Chèque'
    _rec_name = 'composed_name'
    _order = 'composed_name asc'

    number = fields.Integer(
        'Numéro', required=True, readonly=True, group_operator=None)

    bank_id = fields.Many2one('res.bank', string='Banque', required=True)

    composed_name = fields.Char(string="Nom Composé", compute="compute_rec_name", store=True)



    state = fields.Selection(
        [('available', 'Disponible'), ('reserved', 'Réservé'), ('used', 'Utilisé'), ('cancelled', 'Annulé')],
        'Statut', required=True, readonly=False, tracking=True)

    payment_id = fields.Many2one('account.payment', string="Paiement lié", tracking=True)

    libelle = fields.Char(string="Libellé Paiement", compute ="compute_treasury")
    motif = fields.Char(string="Motif utilisation")
    payment_ids = fields.One2many('account.payment', 'checkbook_id', string='Paiement')
    checkbook_id = fields.Many2one('account.check.book', string='Carnet de chèques', ondelete='restrict')

    @api.depends('number', 'bank_id')
    def compute_rec_name(self):
        for rec in self:
            if rec.number and rec.bank_id:
                rec.composed_name = str(rec.number).zfill(7)

    @api.depends('payment_ids')
    def compute_treasury(self):
        libelle = ""
        for rec in self:
            if len(rec.payment_ids) > 0:
                rec.state = 'used'
                rec.payment_id = rec.payment_ids[0].id
                if rec.payment_id.reconciled_invoice_ids:
                    for inv in rec.payment_ids[0].reconciled_invoice_ids:
                        libelle = libelle + ", " + inv.name
                    rec.libelle = libelle
            elif rec.state == 'used' and rec.motif == False:
                rec.state = 'available'
                rec.payment_id = False
                rec.libelle = False
            else:
                rec.payment_id = False
                rec.libelle = False

    def reserve_check(self):
        if self.state == 'available':
            self.state = 'reserved'

    def unreserve_check(self):
        if self.state in ('reserved', 'cancelled'):
            self.state = 'available'
        if self.state == 'used' and not self.payment_id:
            self.state = 'available'
        elif self.state == 'used' and self.payment_id:
            raise UserError("Vous ne pouvez pas liberer un chèque dejà affecté à un paiement!")

    def manual_use_check(self):
        if self.state in ('reserved', 'available'):
            if self.motif != False:
                self.state = 'used'
            else:
                raise UserError("Merci de saisir le motif de l'utilisation manuelle du chèque")

    def cancel_check(self):
        if self.state == 'available':
            self.state = 'cancelled'
        else:
            raise UserError("Vous ne pouvez pas annuler un chèque non disponible!")