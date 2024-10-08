# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class DynamicCheque(models.Model):
    _name = 'dynamic.cheque'
    _description = "Dynamic Cheque"

    name = fields.Char(string="Cheque Format", required=True)
    partner_id = fields.Char(string="Partner")
    cheque_height = fields.Float(string='Height')
    cheque_width = fields.Float(string='Width')
    top_margin = fields.Float(string="Top Margin")
    left_margin = fields.Float(string='Left Margin')
    font_size = fields.Float(string="Font Size")
    char_spacing = fields.Float(string="Character Spacing")
    payee_top_margin = fields.Float(string='Top Margin')
    payee_left_margin = fields.Float(string='Left Margin')
    payee_width = fields.Float(string="Width")
    payee_font_size = fields.Float(string="Font Size")
    af_top_margin = fields.Float(string='Top Margin')
    af_left_margin = fields.Float(string='Left Margin')
    af_width = fields.Float(string="Width")
    af_font_size = fields.Float(string="Font Size")
    first_line_amount = fields.Char(string='First Line')
    second_line_amount = fields.Char(string='Second Line')
    fl_top_margin = fields.Float(string='First Line Top Margin')
    fl_left_margin = fields.Float(string='First Line Left Margin')
    fl_width = fields.Float(string="First Line Width")
    words_in_fl_line = fields.Integer(string="No. of Word in First Line")
    sc_top_margin = fields.Float(string='Second Line Top Margin')
    sc_left_margin = fields.Float(string='Second Line Left Margin')
    sc_width = fields.Float(string='Second Line Width')
    words_in_sc_line = fields.Integer(string='No. of Word in Second Line')
    sc_font_size = fields.Float(string='Font Size')
    journal_id = fields.Many2one('account.journal', string='Journal')
    full_left_margin = fields.Float(string='Marge Gauche du Chèque', default=418)
    full_top_margin = fields.Float(string='Marge Top du Chèque', default=228)

