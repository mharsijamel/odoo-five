from odoo import fields, models, api, _


class ProjectProject(models.Model):

    _inherit = 'project.project'

    state = fields.Selection([('todo','To Do'),('open', 'Open'), ('closed', 'Closed'),('cancel','Cancel')],  string='Status', readonly=True, copy=False, index=True, tracking=True, default='todo')

    post_installation_id = fields.Many2one('post.installation', string='Post Installation', copy=False)


    def def_get_project_team_leaders(self):
        team_leaders = []
        if self.team_id:
            team = self.team_id
            if team.user_id:
                team_leaders.append(team.user_id.id)
            if team.site_foreman_id:
                team_leaders.append(team.site_foreman_id.id)
        return team_leaders
    def action_close(self):
        self.ensure_one()
        team_leaders = self.def_get_project_team_leaders()
        today = fields.Date.today()
        vals = {
            'name': self.name + ' - ' + 'Post Installation',
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
            'partner_id': self.partner_id.id,
            'deposit_date': today,
        }

        post_installation = self.env['post.installation'].sudo().create(vals)
        if team_leaders:
            for leader in team_leaders:
                self.activity_schedule(
                    'post_installation.mail_activity_project_project',
                    note=_('Project closed by %s , Please select a respensible for post installation') % (self.user_id.name,),
                    user_id=leader,)
        self.state = 'closed'
        self.post_installation_id = post_installation.id

        return post_installation



    def action_open(self):
        self.state = 'open'

    def action_cancel(self):
        self.state = 'cancel'

    def action_todo(self):
        self.state = 'todo'