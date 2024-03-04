from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):

    _inherit = 'account.journal'


    incash_check = fields.Boolean(string="In Cash Check")

    incash_treaty = fields.Boolean(string="In Cash Treaty")

    inpayed_check = fields.Boolean(string="In Payed Check")

    inpayed_treaty = fields.Boolean(string="In Payed Treaty")



    @api.constrains('incash_check', 'incash_treaty', 'inpayed_check', 'inpayed_treaty')
    def _check_ony_one_selcted(self):
        for journal in self :
            if journal.incash_check == True:
                if journal.incash_treaty or journal.inpayed_check or journal.inpayed_treaty:
                    raise UserError(_("You can't select more than one option"))
            if journal.incash_treaty == True:
                if journal.incash_check or journal.inpayed_check or journal.inpayed_treaty:
                    raise UserError(_("You can't select more than one option"))
            if journal.inpayed_check == True:
                if journal.incash_treaty or journal.incash_check or journal.inpayed_treaty:
                    raise UserError(_("You can't select more than one option"))
            if journal.inpayed_treaty == True:
                if journal.incash_treaty or journal.inpayed_check or journal.incash_check:
                    raise UserError(_("You can't select more than one option"))
