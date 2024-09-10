from odoo import api, fields, models


import logging
_logger = logging.getLogger(__name__)
class Employee(models.Model):
    _inherit = "hr.employee"


    # Define the currency field
    currency_id = fields.Many2one('res.currency', string='Currency')

    # Define the salary field
    salary = fields.Monetary(string='Salaire', currency_field='currency_id', track_visibility='onchange')
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        ondelete='set null',  # Set this to cascade the deletion
    )
    child_analytic_account_ids = fields.One2many(
        comodel_name="account.analytic.account",
        compute='_compute_child_analytic_accounts',
        string="Child Analytic Accounts",
    )
    current_month_balance = fields.Monetary(
        string='Balance du mois Encours', 
        compute='_compute_current_month_balance',
        currency_field='currency_id',
    )

    @api.depends('analytic_account_id')
    def _compute_current_month_balance(self):
        for employee in self:
            if employee.analytic_account_id:
                employee.current_month_balance = employee.analytic_account_id.get_current_month_balance()
            else:
                employee.current_month_balance = 0.0

    def _compute_child_analytic_accounts(self):
        for employee in self:
            if employee.analytic_account_id:
                # Search for child accounts excluding the parent account itself
                child_accounts = self.env['account.analytic.account'].search([
                    ('parent_id', 'child_of', employee.analytic_account_id.id),
                    ('id', '!=', employee.analytic_account_id.id)
                ])
                employee.child_analytic_account_ids = child_accounts
            else:
                employee.child_analytic_account_ids = False
    @api.model
    def create(self, vals):
        employee = super(Employee, self).create(vals)
        if 'analytic_account_id' in vals:
            analytic_account = self.env['account.analytic.account'].browse(vals['analytic_account_id'])
            if analytic_account.employee_id != employee:
                analytic_account.employee_id = employee
            if 'salary' in vals:
                employee.update_analytic_distribution_salary()
        return employee

    def write(self, vals):
        res = super(Employee, self).write(vals)
        if 'analytic_account_id' in vals:
            analytic_account = self.env['account.analytic.account'].browse(vals['analytic_account_id'])
            if analytic_account.employee_id != self:
                analytic_account.employee_id = self
        if 'salary' in vals:
            _logger.info("salaire test")
            self.update_analytic_distribution_salary()
        return res
    
    def unlink(self):
        for employee in self:
            employee.update_analytic_distribution_salary(delete=True)
        return super(Employee, self).unlink()

    def update_analytic_distribution_salary(self, delete=False):
        _logger.info("okokok")
        salary_tag = self.env['account.analytic.tag'].search([('name', '=', 'SALAIRE')], limit=1)
        tag_id = salary_tag.id
        _logger.info("tag_id: %s", tag_id)
        distributions = self.env['account.analytic.distribution'].search([('tag_id', '=', tag_id)])
        distributions.unlink()
        total_salary = sum(employee.salary for employee in self.env['hr.employee'].search([]))
        _logger.info("total: %s", total_salary)
        employees = self.env['hr.employee'].search([])
        for employee in employees:
            percentage = (employee.salary / total_salary) * 100
            _logger.info("name: %s", employee.name)
            _logger.info("pourcentage: %s", percentage)

            if employee.analytic_account_id and employee.analytic_account_id.id:
                _logger.info("named: %s", employee.name)
                self.env['account.analytic.distribution'].create({
                    'account_id': employee.analytic_account_id.id,
                    'tag_id': tag_id,
                    'percentage': percentage
                })