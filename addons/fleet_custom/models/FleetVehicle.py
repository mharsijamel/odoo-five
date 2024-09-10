from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        ondelete='set null',  # Set this to cascade the deletion
    )
    assurance = fields.Monetary(string="Assurance", track_visibility='onchange' )
    carburant = fields.Monetary(string="CARBURANT", track_visibility='onchange' )
    taxe = fields.Monetary(string="TAXE", track_visibility='onchange' )
    @api.model
    def create(self, vals):
        vehicle = super(FleetVehicle, self).create(vals)
        if 'assurance' and vals['assurance'] != 0 in vals:
            vehicle.update_analytic_distribution()
        if 'carburant' in vals and vals['carburant'] != 0:
            vehicle.update_analytic_distribution_carburant()
        if 'taxe' in vals and vals['taxe'] != 0:
            vehicle.update_analytic_distribution_taxe()
        if 'analytic_account_id' in vals:
            analytic_account = self.env['account.analytic.account'].browse(vals['analytic_account_id'])
            if analytic_account.vehicle_id != vehicle:
                analytic_account.vehicle_id = vehicle
        return vehicle

    def write(self, vals):
        result = super(FleetVehicle, self).write(vals)
        if 'assurance' in vals:
            self.update_analytic_distribution()
        if 'carburant' in vals:
            self.update_analytic_distribution_carburant()
        if 'taxe' in vals:
            self.update_analytic_distribution_taxe()
        if 'analytic_account_id' in vals:
            analytic_account = self.env['account.analytic.account'].browse(vals['analytic_account_id'])
            if analytic_account.vehicle_id != self:
                analytic_account.vehicle_id = self
        if 'driver_id' in vals:
            self._update_employee_vehicle()
        return result

    def unlink(self):
        for vehicle in self:
            vehicle.update_analytic_distribution(delete=True)
            vehicle.update_analytic_distribution_carburant(delete=True)
            vehicle.update_analytic_distribution_taxe(delete=True)
        return super(FleetVehicle, self).unlink()
    
    def update_analytic_distribution(self, delete=False):
        assurance_tag = self.env['account.analytic.tag'].search([('name', '=', 'ASSURANCE')], limit=1)
        tag_id = assurance_tag.id
        distributions = self.env['account.analytic.distribution'].search([('tag_id', '=', tag_id)])
        distributions.unlink()
        total_assurance = sum(vehicle.assurance for vehicle in self.env['fleet.vehicle'].search([]))
        _logger.info("total: %s", total_assurance)
        vehicles = self.env['fleet.vehicle'].search([])
        for vehicle in vehicles:
            percentage = (vehicle.assurance / total_assurance) * 100
            _logger.info("pourcentage: %s", percentage)

            self.env['account.analytic.distribution'].create({
                'account_id': vehicle.analytic_account_id.id,
                'tag_id': tag_id,
                'percentage': percentage
            })
        
    
    def update_analytic_distribution_carburant(self, delete=False):
        carburant_tag = self.env['account.analytic.tag'].search([('name', '=', 'CARBURANT')], limit=1)
        tag_id = carburant_tag.id
        distributions = self.env['account.analytic.distribution'].search([('tag_id', '=', tag_id)])
        distributions.unlink()
        total_carburant = sum(vehicle.carburant for vehicle in self.env['fleet.vehicle'].search([]))
        _logger.info("total: %s", total_carburant)
        vehicles = self.env['fleet.vehicle'].search([])
        for vehicle in vehicles:
            percentage = (vehicle.carburant / total_carburant) * 100
            _logger.info("pourcentage: %s", percentage)

            self.env['account.analytic.distribution'].create({
                'account_id': vehicle.analytic_account_id.id,
                'tag_id': tag_id,
                'percentage': percentage
            })

    def update_analytic_distribution_taxe(self, delete=False):
        taxe_tag = self.env['account.analytic.tag'].search([('name', '=', 'TAXE')], limit=1)
        tag_id = taxe_tag.id
        distributions = self.env['account.analytic.distribution'].search([('tag_id', '=', tag_id)])
        distributions.unlink()
        total_taxe = sum(vehicle.taxe for vehicle in self.env['fleet.vehicle'].search([]))
        _logger.info("total: %s", total_taxe)
        vehicles = self.env['fleet.vehicle'].search([])
        for vehicle in vehicles:
            percentage = (vehicle.taxe / total_taxe) * 100
            _logger.info("pourcentage: %s", percentage)

            self.env['account.analytic.distribution'].create({
                'account_id': vehicle.analytic_account_id.id,
                'tag_id': tag_id,
                'percentage': percentage
            })

    def _update_employee_vehicle(self):
        if self.driver_id:
            partner = self.driver_id
            _logger.info("Processing partner: %s", partner.id)

            user = self.env['res.users'].search([('email', '=', partner.email)], limit=1)
            _logger.info("Processing partner: %s", user.id)

            employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
            if self.analytic_account_id:
                self.analytic_account_id.parent_id = employee.analytic_account_id
                self.analytic_account_id.group_id = employee.analytic_account_id.group_id
            old_employee = self.env['hr.employee'].search([('vehicle_id', '=', self.id)], limit=1)
            if old_employee:
                old_employee.write({'vehicle_id': False})
            if employee:
                _logger.info("Processing employee: %s", employee.id)
                employee.write({'vehicle_id': self.id})
            else:
                _logger.warning("No employee found for user %s", user.id)