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

def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != '15.0': raise Warning('Module support Odoo series 15.0 found {}.'.format(server_serie))
    return True
