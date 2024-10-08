from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    account_check_printing_layout = fields.Selection(
        selection_add=[
            (
                "account_check_printing_report_dlt103.action_report_check_dlt103",
                "BIAT",
            ),
            (
                "account_check_printing_report_dlt103.action_report_check_zitouna",
                "ZITOUNA",
            )
            ,
            (
                "account_check_printing_report_dlt103.action_report_check_wifak",
                "WIFAK",
            ),
            (
                "account_check_printing_report_dlt103.action_report_check_baraka",
                "BARAKA",
            )
        ],
        ondelete={
            "account_check_printing_report_dlt103.action_report_check_dlt103": "cascade",
            "account_check_printing_report_dlt103.action_report_check_zitouna": "cascade",
            "account_check_printing_report_dlt103.action_report_check_wifak": "cascade",
            "account_check_printing_report_dlt103.action_report_check_baraka": "cascade"
        },
    )
