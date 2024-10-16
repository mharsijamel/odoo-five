# -*- coding: utf-8 -*-
#############################################################################
#
#    Infotech Consulting Services Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Infotech Consulting Services(<https://www.ics-tunisie.com>)
#    Author: Infotech Consulting Services(<http://www.ics-tunisie.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################


# -------------------------------------------------------------
# French
# -------------------------------------------------------------


to_19_fr = ('Zéro', 'Un', 'Deux', 'Trois', 'Quatre', 'Cinq', 'Six',
            'Sept', 'Huit', 'Neuf', 'Dix', 'Onze', 'Douze', 'Treize',
            'Quatorze', 'Quinze', 'Seize', 'Dix-sept', 'Dix-huit', 'Dix-neuf')
tens_fr = ('Vingt', 'Trente', 'Quarante', 'Cinquante', 'Soixante', 'Soixante-dix', 'Quatre-vingts', 'Quatre-vingt Dix')
denom_fr = ('',
            'Mille', 'Millions', 'Milliards', 'Billions', 'Quadrillions',
            'Quintillion', 'Sextillion', 'Septillion', 'Octillion', 'Nonillion',
            'Décillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quattuordecillion',
            'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Icosillion', 'Vigintillion')


def _convert_nn_fr(val):
    """ convert a value < 100 to French
    """
    if val < 20:
        return to_19_fr[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_fr)):
        if dval + 10 > val:
            if dval == 70:
                return tens_fr[4] + ' ' + to_19_fr[(val % 10) + 10]
            if dval == 90:
                return tens_fr[6] + ' ' + to_19_fr[(val % 10) + 10]
            if val % 10:
                return dcap + '-' + to_19_fr[val % 10]
            return dcap


def _convert_nnn_fr(val):
    """ convert a value < 1000 to french

        special cased because it is the level that kicks
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        if rem == 1:
            word = ' Cent'
        else:
            word = to_19_fr[rem] + ' Cent'
        if mod > 0:
            word = word + ' '
    if mod > 0:
        word = word + _convert_nn_fr(mod)
    return word


def french_number(val):
    if val < 100:
        return _convert_nn_fr(val)
    if val < 1000:
        return _convert_nnn_fr(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_fr))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn_fr(l) + ' ' + denom_fr[didx]
            if r > 0:
                ret = ret + ', ' + french_number(r)
            return ret


def amount_to_text_fr(number, currency):
    number = '%.3f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = french_number(abs(int(list[0])))
    end_word = french_number(int(list[1]))
    cents_number = int(list[1])
    cents_name = (cents_number > 1) and ' Millimes' or ' Millime'
    final_result = start_word + ' ' + units_name + ' ' + end_word + ' ' + cents_name
    return final_result


# -------------------------------------------------------------
# Dutch
# -------------------------------------------------------------

to_19_nl = ('Nul', 'Een', 'Twee', 'Drie', 'Vier', 'Vijf', 'Zes',
            'Zeven', 'Acht', 'Negen', 'Tien', 'Elf', 'Twaalf', 'Dertien',
            'Veertien', 'Vijftien', 'Zestien', 'Zeventien', 'Achttien', 'Negentien')
tens_nl = ('Twintig', 'Dertig', 'Veertig', 'Vijftig', 'Zestig', 'Zeventig', 'Tachtig', 'Negentig')
denom_nl = ('',
            'Duizend', 'Miljoen', 'Miljard', 'Triljoen', 'Quadriljoen',
            'Quintillion', 'Sextiljoen', 'Septillion', 'Octillion', 'Nonillion',
            'Decillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quattuordecillion',
            'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion')


def _convert_nn_nl(val):
    """ convert a value < 100 to Dutch
    """
    if val < 20:
        return to_19_nl[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_nl)):
        if dval + 10 > val:
            if val % 10:
                return dcap + '-' + to_19_nl[val % 10]
            return dcap


def _convert_nnn_nl(val):
    """ convert a value < 1000 to Dutch

        special cased because it is the level that kicks
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        word = to_19_nl[rem] + ' Honderd'
        if mod > 0:
            word = word + ' '
    if mod > 0:
        word = word + _convert_nn_nl(mod)
    return word


def dutch_number(val):
    if val < 100:
        return _convert_nn_nl(val)
    if val < 1000:
        return _convert_nnn_nl(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_nl))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn_nl(l) + ' ' + denom_nl[didx]
            if r > 0:
                ret = ret + ', ' + dutch_number(r)
            return ret


def amount_to_text_nl(number, currency):
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = dutch_number(int(list[0]))
    end_word = dutch_number(int(list[1]))
    cents_number = int(list[1])
    cents_name = (cents_number > 1) and 'cent' or 'cent'
    final_result = start_word + ' ' + units_name + ' ' + end_word + ' ' + cents_name
    return final_result


# -------------------------------------------------------------
# Generic functions
# -------------------------------------------------------------

_translate_funcs = {'fr': amount_to_text_fr, 'nl': amount_to_text_nl}


def add_amount_to_text_function(lang, func):
    _translate_funcs[lang] = func


# TODO: we should use the country AND language (ex: septante VS soixante dix)
# TODO: we should use en by default, but the translation func is yet to be implemented
def amount_to_text(nbr, lang='fr', currency='Dinars'):
    """ Converts an integer to its textual representation, using the language set in the context if any.

        Example::

            1654: mille six cent cinquante-quatre.
    """
    #    if nbr > 1000000:
    ##TODO: use logger
    #        print "WARNING: number too large '%d', can't translate it!" % (nbr,)
    #        return str(nbr)
    if not _translate_funcs.has_key(lang):
        # TODO: (default should be en) same as above
        lang = 'fr'
    return _translate_funcs[lang](abs(nbr), currency)


if __name__ == '__main__':
    from sys import argv

    lang = 'nl'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
