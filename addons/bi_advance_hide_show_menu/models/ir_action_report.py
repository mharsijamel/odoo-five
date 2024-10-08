# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import json
import werkzeug
from lxml import etree
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from odoo.http import request

class IrActionReport(models.Model):
    _inherit="ir.actions.report"
    _description = 'Ir Action Report'

    group_ids = fields.Many2many('res.groups', string='Groups')
    users_ids = fields.Many2many('res.users', string='Users')

class FieldConfiguration(models.Model):
    _name = 'field.config'
    _description = 'Field Configuration'

    config_fields_id = fields.Many2one('ir.model', string='Fields')
    fields_id = fields.Many2one('ir.model.fields', string='Field')
    name = fields.Char(string='Technical Name', related='fields_id.name')
    group_ids = fields.Many2many('res.groups', string='Groups')
    readonly = fields.Boolean(string='Readonly')
    invisible = fields.Boolean(string='Invisible')

class IrModel(models.Model):
    _inherit= "ir.model"
    _description = 'Ir Model'

    field_config_id = fields.One2many('field.config','config_fields_id', string='Field Config')

    
class View(models.Model):
    _inherit = 'ir.ui.view'
    _description = 'View'

    def _apply_groups(self, node, name_manager, node_info):
        """Apply group restrictions,  may be set at view level or model level::
           * at view level this means the element should be made invisible to
             people who are not members
           * at model level (exclusively for fields, obviously), this means
             the field should be completely removed from the view, as it is
             completely unavailable for non-members

           :return: True if field should be included in the result of fields_view_get
        """
        if node.get('groups'):
            can_see = self.user_has_groups(groups=node.get('groups'))
            if not can_see:
                node.set('invisible', '1')
                node_info['modifiers']['invisible'] = True
                if 'attrs' in node.attrib:
                    del node.attrib['attrs']
            del node.attrib['groups']
        models = []

        Models = self.env['ir.model'].search([('field_config_id', '!=',False)])
        
        for required_model in Models:
            if len(required_model.field_config_id) > 0 :
                models.append(required_model)
                

        for Model in models:
                    
            field_name = None
            if node.tag == "field":
                field_name = node.get("name")
            elif node.tag == "label":
                field_name = node.get("for")
            if field_name and field_name in Model._fields:
                field = Model._fields[field_name]
                if field.groups and not self.user_has_groups(groups=field.groups):
                    node.getparent().remove(node)
                    fields.pop(field_name, None)
                    # no point processing view-level ``groups`` anymore, return
                    return False
            
              
            ir_model_obj = self.env['ir.model'].search([])
            for i in ir_model_obj:
                if i.field_config_id:
                    for field_line in i.field_config_id:
                        if not field_line.group_ids:
                            if field_name == field_line.fields_id.name and Model.model == field_line.fields_id.model:
                                if field_line.invisible == True:
                                    node.set('invisible', '1')
                                if field_line.readonly == True:
                                    node.set('readonly', '1')
                        if field_line.group_ids:
                            for group in field_line.group_ids:
                                if group.users:
                                    for user in group.users:
                                        if user.id == self.env.uid:
                                            if field_name == field_line.fields_id.name and Model.model == field_line.fields_id.model:
                                                if field_line.invisible == True:
                                                    node.set('invisible', '1') 
                                                if field_line.readonly == True:
                                                    node.set('readonly', '1')   
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: