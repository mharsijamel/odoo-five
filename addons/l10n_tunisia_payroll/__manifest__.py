# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Paie - Tunisia",
    "version": "15.0.1.1",
    'description':  """Tunisian Payroll Rules Basic Version.
    ======================
    
        - Configuration of hr_payroll for Tunisian localization
        - Basic configuration for newly installed company
        - Absence - Advances - CNSS 
        - Important: you need to fill the wage amount for the employee in the contract and chose tunisia payroll from the structure field.
        """,
    "category": "Human Resources",
    "website": "",
    "sequence": 38,
    "summary": "Manage your employee payroll records",
    'images': ['static/description/Banner.jpg'],
    "license": "LGPL-3",
    "author": "Ahmed Mnasri",
    "depends": ["hr_contract", "hr_holidays"],
    "data": [
        "security/hr_payroll_security.xml",
        "security/ir.model.access.csv",
        "data/hr_payroll_sequence.xml",
        "data/hr_payroll_data.xml",
        "wizard/hr_payroll_contribution_register_report_views.xml",
        "wizard/hr_payroll_payslips_by_employees_views.xml",
        "views/menus.xml",
        "views/hr_contract_views.xml",
        "views/hr_contract_advantage_views.xml",
        "views/hr_payroll_structure_views.xml",
        "views/hr_salary_rule_category_views.xml",
        "views/hr_contribution_register_views.xml",
        "views/hr_salary_rule_views.xml",
        "views/hr_payslip_line_views.xml",
        "views/hr_payslip_views.xml",
        "views/hr_payslip_run_views.xml",
        "views/hr_employee_views.xml",
        "views/report_contributionregister.xml",
        "views/report_payslip.xml",
        "views/report_payslipdetails.xml",
        "report/report.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml"
    ],
    "application": True,
}
