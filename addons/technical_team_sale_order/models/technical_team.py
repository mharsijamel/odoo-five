from odoo import exceptions, fields, models, api, _

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError
from odoo.release import version



class TechnicalTeamMember(models.Model):
    _name = 'technical.team.member'
    _inherit = ['mail.thread']
    _description = 'Technical Sales Team Member'
    _rec_name = 'user_id'
    _order = 'create_date ASC'
    _check_company_auto = True

    technical_team_id = fields.Many2one(
        'technical.team', string='Technical Sales Team',
        default=False,  # TDE: temporary fix to activate depending computed fields
        check_company=True, index=True, ondelete="cascade", required=True)
    user_id = fields.Many2one(
        'res.users', string='Technical Person',  # TDE FIXME check responsible field
        check_company=True, index=True, ondelete='cascade', required=True,
        domain="[('share', '=', False), ('id', 'not in', user_in_teams_ids), ('company_ids', 'in', user_company_ids)]")
    user_in_teams_ids = fields.Many2many(
        'res.users', compute='_compute_user_in_teams_ids',
        help='UX: Give users not to add in the currently chosen team to avoid duplicates')
    user_company_ids = fields.Many2many(
        'res.company', compute='_compute_user_company_ids',
        help='UX: Limit to team company or all if no company')
    active = fields.Boolean(string='Active', default=True)
    is_membership_multi = fields.Boolean(
        'Multiple Memberships Allowed', compute='_compute_is_membership_multi',
        help='If True, users may belong to several sales teams. Otherwise membership is limited to a single sales team.')
    member_warning = fields.Text(compute='_compute_member_warning')
    # salesman information
    image_1920 = fields.Image("Image", related="user_id.image_1920", max_width=1920, max_height=1920)
    image_128 = fields.Image("Image (128)", related="user_id.image_128", max_width=128, max_height=128)
    name = fields.Char(string='Name', related='user_id.display_name', readonly=False)
    email = fields.Char(string='Email', related='user_id.email')
    phone = fields.Char(string='Phone', related='user_id.phone')
    mobile = fields.Char(string='Mobile', related='user_id.mobile')
    company_id = fields.Many2one('res.company', string='Company', related='user_id.company_id')

    @api.constrains('technical_team_id', 'user_id', 'active')
    def _constrains_membership(self):
        # In mono membership mode: check technical_team_id / user_id is unique for active
        # memberships. Inactive memberships can create duplicate pairs which is whyy
        # we don't use a SQL constraint. Include "self" in search in case we use create
        # multi with duplicated user / team pairs in it. Use an explicit active leaf
        # in domain as we may have an active_test in context that would break computation
        existing = self.env['technical.team.member'].search([
            ('technical_team_id', 'in', self.technical_team_id.ids),
            ('user_id', 'in', self.user_id.ids),
            ('active', '=', True)
        ])
        duplicates = self.env['technical.team.member']

        active_records = dict(
            (membership.user_id.id, membership.technical_team_id.id)
            for membership in self if membership.active
        )
        for membership in self:
            potential = existing.filtered(lambda m: m.user_id == membership.user_id and \
                m.technical_team_id == membership.technical_team_id and m.id != membership.id
            )
            if not potential or len(potential) > 1:
                duplicates += potential
                continue
            if active_records.get(potential.user_id.id):
                duplicates += potential
            else:
                active_records[potential.user_id.id] = potential.technical_team_id.id

        if duplicates:
            raise exceptions.ValidationError(
                _("You are trying to create duplicate membership(s). We found that %(duplicates)s already exist(s).",
                  duplicates=", ".join("%s (%s)" % (m.user_id.name, m.technical_team_id.name) for m in duplicates)
                 ))

    @api.depends('technical_team_id', 'is_membership_multi', 'user_id')
    @api.depends_context('default_technical_team_id')
    def _compute_user_in_teams_ids(self):
        """ Give users not to add in the currently chosen team to avoid duplicates.
        In multi membership mode this field is empty as duplicates are allowed. """
        if all(m.is_membership_multi for m in self):
            member_user_ids = self.env['res.users']
        elif self.ids:
            member_user_ids = self.env['technical.team.member'].search([('id', 'not in', self.ids)]).user_id
        else:
            member_user_ids = self.env['technical.team.member'].search([]).user_id
        for member in self:
            if member_user_ids:
                member.user_in_teams_ids = member_user_ids
            elif member.technical_team_id:
                member.user_in_teams_ids = member.technical_team_id.member_ids
            elif self.env.context.get('default_technical_team_id'):
                member.user_in_teams_ids = self.env['technical.team'].browse(self.env.context['default_technical_team_id']).member_ids
            else:
                member.user_in_teams_ids = self.env['res.users']

    @api.depends('technical_team_id')
    def _compute_user_company_ids(self):
        all_companies = self.env['res.company'].search([])
        for member in self:
            member.user_company_ids = member.technical_team_id.company_id or all_companies

    @api.depends('technical_team_id')
    def _compute_is_membership_multi(self):
        multi_enabled = self.env['ir.config_parameter'].sudo().get_param('sales_team.membership_multi', False)
        self.is_membership_multi = multi_enabled

    @api.depends('is_membership_multi', 'active', 'user_id', 'technical_team_id')
    def _compute_member_warning(self):
        """ Display a warning message to warn user they are about to archive
        other memberships. Only valid in mono-membership mode and take into
        account only active memberships as we may keep several archived
        memberships. """
        if all(m.is_membership_multi for m in self):
            self.member_warning = False
        else:
            active = self.filtered('active')
            (self - active).member_warning = False
            if not active:
                return
            existing = self.env['technical.team.member'].search([('user_id', 'in', active.user_id.ids)])
            user_mapping = dict.fromkeys(existing.user_id, self.env['technical.team'])
            for membership in existing:
                user_mapping[membership.user_id] |= membership.technical_team_id

            for member in active:
                teams = user_mapping.get(member.user_id, self.env['technical.team'])
                remaining = teams - (member.technical_team_id | member._origin.technical_team_id)
                if remaining:
                    member.member_warning = _("Adding %(user_name)s in this team would remove him/her from its current teams %(team_names)s.",
                                              user_name=member.user_id.name,
                                              team_names=", ".join(remaining.mapped('name'))
                                             )
                else:
                    member.member_warning = False


    @api.model_create_multi
    def create(self, values_list):
        """ Specific behavior implemented on create

          * mono membership mode: other user memberships are automatically
            archived (a warning already told it in form view);
          * creating a membership already existing as archived: do nothing as
            people can manage them from specific menu "Members";
        """
        is_membership_multi = self.env['ir.config_parameter'].sudo().get_param('sales_team.membership_multi', False)
        if not is_membership_multi:
            self._synchronize_memberships(values_list)
        return super(TechnicalTeamMember, self).create(values_list)

    def write(self, values):
        """ Specific behavior about active. If you change user_id / team_id user
        get warnings in form view and a raise in constraint check. We support
        archive / activation of memberships that toggles other memberships. But
        we do not support manual creation or update of user_id / team_id. This
        either works, either crashes). Indeed supporting it would lead to complex
        code with low added value. Users should create or remove members, and
        maybe archive / activate them. Updating manually memberships by
        modifying user_id or team_id is advanced and does not benefit from our
        support. """
        is_membership_multi = self.env['ir.config_parameter'].sudo().get_param('sales_team.membership_multi', False)
        if not is_membership_multi and values.get('active'):
            self._synchronize_memberships([
                dict(user_id=membership.user_id.id, technical_team_id=membership.technical_team_id.id)
                for membership in self
            ])
        return super(TechnicalTeamMember, self).write(values)

    def _synchronize_memberships(self, user_team_ids):
        """ Synchronize memberships: archive other memberships.

        :param user_team_ids: list of pairs (user_id, technical_team_id)
        """
        existing = self.search([
            ('active', '=', True),  # explicit search on active only, whatever context
            ('user_id', 'in', [values['user_id'] for values in user_team_ids])
        ])
        user_memberships = dict.fromkeys(existing.user_id.ids, self.env['technical.team.member'])
        for membership in existing:
            user_memberships[membership.user_id.id] += membership

        existing_to_archive = self.env['technical.team.member']
        for values in user_team_ids:
            existing_to_archive += user_memberships.get(values['user_id'], self.env['technical.team.member']).filtered(
                lambda m: m.technical_team_id.id != values['technical_team_id']
            )

        if existing_to_archive:
            existing_to_archive.action_archive()

        return existing_to_archive


class TechnicalTeam(models.Model):
    _name = "technical.team"
    _inherit = ['mail.thread']
    _description = "Technical Sales Team"
    _order = "sequence ASC, create_date DESC, id DESC"
    _check_company_auto = True

    def _get_default_team_id(self, user_id=None, domain=None):
        """ Compute default team id for sales related documents. Note that this
        method is not called by default_get as it takes some additional
        parameters and is meant to be called by other default methods.

        Heuristic (when multiple match: take from default context value or first
        sequence ordered)

          1- any of my teams (member OR responsible) matching domain, either from
             context or based on _order;
          2- any of my teams (member OR responsible), either from context or based
             on _order;
          3- default from context
          4- any team matching my company and domain (based on company rule)
          5- any team matching my company (based on company rule)

        Note: ResPartner.team_id field is explicitly not taken into account. We
        think this field causes a lot of noises compared to its added value.
        Think notably: team not in responsible teams, team company not matching
        responsible or lead company, asked domain not matching, ...

        :param user_id: salesperson to target, fallback on env.uid;
        :domain: optional domain to filter teams (like use_lead = True);
        """
        if user_id is None:
            user = self.env.user
        else:
            user = self.env['res.users'].sudo().browse(user_id)
        default_team = self.env['technical.team'].browse(
            self.env.context['default_team_id']
        ) if self.env.context.get('default_team_id') else self.env['technical.team']
        valid_cids = [False] + [c for c in user.company_ids.ids if c in self.env.companies.ids]

        # 1- find in user memberships - note that if current user in C1 searches
        # for team belonging to a user in C1/C2 -> only results for C1 will be returned
        team = self.env['technical.team']
        teams = self.env['technical.team'].search([
            ('company_id', 'in', valid_cids),
            '|', ('user_id', '=', user.id), ('member_ids', 'in', [user.id])
        ])
        if teams and domain:
            filtered_teams = teams.filtered_domain(domain)
            if default_team and default_team in filtered_teams:
                team = default_team
            else:
                team = filtered_teams[:1]

        # 2- any of my teams
        if not team:
            if default_team and default_team in teams:
                team = default_team
            else:
                team = teams[:1]

        # 3- default: context
        if not team and default_team:
            team = default_team

        if not team:
            teams = self.env['technical.team'].search([('company_id', 'in', valid_cids)])
            # 4- default: based on company rule, first one matching domain
            if teams and domain:
                team = teams.filtered_domain(domain)[:1]
            # 5- default: based on company rule, first one
            if not team:
                team = teams[:1]

        return team

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    name = fields.Char('Technical Sales Team', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean(default=True,
                            help="If the active field is set to false, it will allow you to hide the Sales Team without removing it.")
    company_id = fields.Many2one(
        'res.company', string='Company', index=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        "res.currency", string="Currency",
        related='company_id.currency_id', readonly=True)
    user_id = fields.Many2one('res.users', string='Team Leader', check_company=True)
    # memberships
    is_membership_multi = fields.Boolean(
        'Multiple Memberships Allowed', compute='_compute_is_membership_multi',
        help='If True, users may belong to several sales teams. Otherwise membership is limited to a single sales team.')

    member_ids = fields.Many2many(
        'res.users', string='Salespersons',
        domain="['&', ('share', '=', False), ('company_ids', 'in', member_company_ids)]",
        compute='_compute_member_ids', inverse='_inverse_member_ids', search='_search_member_ids',
        help="Users assigned to this team.")
    member_company_ids = fields.Many2many(
        'res.company', compute='_compute_member_company_ids',
        help='UX: Limit to team company or all if no company')

    technical_team_member_ids = fields.One2many(
        'technical.team.member', 'technical_team_id', string='Sales Team Members',
        help="Add members to automatically assign their documents to this sales team.")
    technical_team_member_all_ids = fields.One2many(
        'technical.team.member', 'technical_team_id', string='Sales Team Members (incl. inactive)',
        context={'active_test': False})
    member_warning = fields.Text('Membership Issue Warning', compute='_compute_member_warning')
    favorite_user_ids = fields.Many2many(
        'res.users', 'technical_team_favorite_user_rel', 'team_id', 'user_id',
        string='Favorite Members', default=_get_default_favorite_user_ids)

    @api.depends('sequence')  # TDE FIXME: force compute in new mode
    def _compute_is_membership_multi(self):
        multi_enabled = self.env['ir.config_parameter'].sudo().get_param('sales_team.membership_multi', False)
        self.is_membership_multi = multi_enabled


    @api.depends('technical_team_member_ids.active')
    def _compute_member_ids(self):
        for team in self:
            team.member_ids = team.technical_team_member_ids.user_id

    def _inverse_member_ids(self):
        for team in self:
            # pre-save value to avoid having _compute_member_ids interfering
            # while building membership status
            memberships = team.technical_team_member_ids
            users_current = team.member_ids
            users_new = users_current - memberships.user_id

            # add missing memberships
            self.env['technical.team.member'].create([{'technical_team_id': team.id, 'user_id': user.id} for user in users_new])

            # activate or deactivate other memberships depending on members
            for membership in memberships:
                membership.active = membership.user_id in users_current
    def _search_member_ids(self, operator, value):
        return [('technical_team_member_ids.user_id', operator, value)]

    @api.depends('is_membership_multi', 'member_ids')
    def _compute_member_warning(self):
        """ Display a warning message to warn user they are about to archive
        other memberships. Only valid in mono-membership mode and take into
        account only active memberships as we may keep several archived
        memberships. """
        self.member_warning = False
        if all(team.is_membership_multi for team in self):
            return
        # done in a loop, but to be used in form view only -> not optimized
        for team in self:
            member_warning = False
            other_memberships = self.env['technical.team.member'].search([
                ('technical_team_id', '!=', team.id if team.ids else False),  # handle NewID
                ('user_id', 'in', team.member_ids.ids)
            ])
            if other_memberships and len(other_memberships) == 1:
                member_warning = _("Adding %(user_name)s in this team would remove him/her from its current team %(team_name)s.",
                                   user_name=other_memberships.user_id.name,
                                   team_name=other_memberships.technical_team_id.name
                                  )
            elif other_memberships:
                member_warning = _("Adding %(user_names)s in this team would remove them from their current teams (%(team_names)s).",
                                   user_names=", ".join(other_memberships.mapped('user_id.name')),
                                   team_names=", ".join(other_memberships.mapped('technical_team_id.name'))
                                  )
            if member_warning:
                team.member_warning = member_warning + " " + _("To add a Salesperson into multiple Teams, activate the Multi-Team option in settings.")
    @api.depends('company_id')
    def _compute_member_company_ids(self):
        """ Available companies for members. Either team company if set, either
        any company if not set on team. """
        all_companies = self.env['res.company'].search([])
        for team in self:
            team.member_company_ids = team.company_id or all_companies

        @api.model_create_multi
        def create(self, vals_list):
            teams = super(TechnicalTeam, self.with_context(mail_create_nosubscribe=True)).create(vals_list)
            teams.filtered(lambda t: t.member_ids)._add_members_to_favorites()
            return teams

        def write(self, values):
            res = super(TechnicalTeam, self).write(values)
            # manually launch company sanity check
            if values.get('company_id'):
                self.technical_team_member_ids._check_company(fnames=['technical_team_id'])

            if values.get('member_ids'):
                self._add_members_to_favorites()
            return res

