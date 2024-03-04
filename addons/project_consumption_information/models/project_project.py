from  odoo import fields, models, api, _



class ProjectProject(models.Model):

    _inherit = 'project.project'

    project_comsumption_line = fields.One2many('project.comsumption.line', 'project_id', string='comsumption',copy=True,auto_join=True)

    vehicle = fields.Char(string="Vehicle")
    localisation = fields.Text(string="Localisation")

