# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class DynamicTreaty(models.Model):
    _name = 'dynamic.treaty'
    _description = "Dynamic Treaty"

    name = fields.Char(string="treaty Format", required=True)
    partner_id = fields.Char(string="Partner")
    treaty_height = fields.Float(string='Height')
    treaty_width = fields.Float(string='Width')
    ac_pay = fields.Boolean(string="A/c Pay")
    ac_top_margin = fields.Float(string="Top Margin")
    ac_left_margin = fields.Float(string='Left Margin')
    ac_font_size = fields.Float(string='Font Size')
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
    af_currency_symbol = fields.Boolean(string="Currency Symbol")
    af_currency_symbol_position = fields.Selection([('before', 'Before'), ('after', 'After')],
                                                   string="Currency Symbol Position", default='before')
    af2_top_margin = fields.Float(string='Top Margin')
    af2_left_margin = fields.Float(string='Left Margin')
    af2_width = fields.Float(string="Width")
    af2_font_size = fields.Float(string="Font Size")
    af2_currency_symbol = fields.Boolean(string="Currency Symbol")
    af2_currency_symbol_position = fields.Selection([('before', 'Before'), ('after', 'After')],
                                                   string="Currency Symbol Position", default='before')
    first_line_amount = fields.Char(string='First Line')
    second_line_amount = fields.Char(string='Second Line')
    fl_top_margin = fields.Float(string='First Line Top Margin')
    fl_left_margin = fields.Float(string='First Line Left Margin')
    fl_width = fields.Float(string="First Line Width")
    fl2_top_margin = fields.Float(string='First Line Top Margin')
    fl2_left_margin = fields.Float(string='First Line Left Margin')
    fl2_width = fields.Float(string="First Line Width")
    words_in_fl_line = fields.Integer(string="No. of Word in First Line")
    sc_top_margin = fields.Float(string='Second Line Top Margin')
    sc_left_margin = fields.Float(string='Second Line Left Margin')
    sc_width = fields.Float(string='Second Line Width')
    words_in_sc_line = fields.Integer(string='No. of Word in Second Line')
    sc_font_size = fields.Float(string='Font Size')
    sc_currency_name = fields.Boolean(string='Currency Name')
    sc_currency_name_position = fields.Selection([('before', 'Before'), ('after', 'After')],
                                                 string="Currency Name Position", default='before')
    comapny_name = fields.Boolean(string='Company Name')
    comp_font_size = fields.Float(string='Font Size')
    comp_top_margin = fields.Float(string="Top Margin")
    comp_left_margin = fields.Float(string="Left Margin")
    comp_width = fields.Float(string="Company Width")
    sb_width = fields.Float(string='Width')
    sb_hight = fields.Float(string='Height')
    sb_top_margin = fields.Float(string='Top Margin')
    sb_left_margin = fields.Float(string='Left Margin')



    de_top_margin = fields.Float(string='Top Margin')
    de_left_margin = fields.Float(string='Left Margin')
    de_width = fields.Float(string="Width")
    de_font_size = fields.Float(string="Font Size")

    de2_top_margin = fields.Float(string='Top Margin')
    de2_left_margin = fields.Float(string='Left Margin')
    de2_width = fields.Float(string="Width")
    de2_font_size = fields.Float(string="Font Size")

    d_top_margin = fields.Float(string='Top Margin')
    d_left_margin = fields.Float(string='Left Margin')
    d_width = fields.Float(string="Width")
    d_font_size = fields.Float(string="Font Size")

    a_top_margin = fields.Float(string='Top Margin')
    a_left_margin = fields.Float(string='Left Margin')
    a_width = fields.Float(string="Width")
    a_font_size = fields.Float(string="Font Size")

    a2_top_margin = fields.Float(string='Top Margin')
    a2_left_margin = fields.Float(string='Left Margin')
    a2_width = fields.Float(string="Width")
    a2_font_size = fields.Float(string="Font Size")

    le_top_margin = fields.Float(string='Top Margin')
    le_left_margin = fields.Float(string='Left Margin')
    le_width = fields.Float(string="Width")
    le_font_size = fields.Float(string="Font Size")

    rib_top_margin = fields.Float(string='Top Margin')
    rib_left_margin = fields.Float(string='Left Margin')
    rib_width = fields.Float(string="Width")
    rib_font_size = fields.Float(string="Font Size")

    rib2_top_margin = fields.Float(string='Top Margin')
    rib2_left_margin = fields.Float(string='Left Margin')
    rib2_width = fields.Float(string="Width")
    rib2_font_size = fields.Float(string="Font Size")

    payee2_top_margin = fields.Float(string='Top Margin')
    payee2_left_margin = fields.Float(string='Left Margin')
    payee2_width = fields.Float(string="Width")
    payee2_font_size = fields.Float(string="Font Size")

    bank_top_margin = fields.Float(string='Top Margin')
    bank_left_margin = fields.Float(string='Left Margin')
    bank_width = fields.Float(string="Width")
    bank_font_size = fields.Float(string="Font Size")