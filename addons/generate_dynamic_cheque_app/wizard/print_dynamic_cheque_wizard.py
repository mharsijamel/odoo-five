# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


class PrintChequeWizard(models.TransientModel):
    _name = 'dynamic.cheque.wizard'
    _description = "Print Dynamic Cheque"

    @api.model
    def default_get(self, fields):
        """
        Override the default_get method to pre-fill the wizard fields based on the context.
        This method is used to automatically populate the 'payment_id' field of the wizard
        with the active payment record's ID when the wizard is opened.
        :param fields: A list of strings representing the names of the fields for which
                       default values are requested. This parameter is used by the super
                       method and not directly in this override.
        :return: A dictionary containing default values for the wizard fields. Specifically,
                 it updates the 'payment_id' with the ID of the payment record that is currently
                 active (selected by the user before opening the wizard).
        :raises UserError: If no active payment record is found in the context, it raises a
                           UserError indicating that the cheque cannot be printed.
        """

        res = super(PrintChequeWizard, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        payment = self.env[active_model].browse(active_id)
        if payment:
            res.update({
                'payment_id': payment.id
            })
            return res
        else:
            raise UserError(_('Payment Not fount You cannot print Cheque !!!!'))

    payment_id = fields.Many2one('account.payment', string='Payment Id')
    journal_id = fields.Many2one('account.journal', related="payment_id.journal_id", string='Journal')
    cheque_format = fields.Many2one('dynamic.cheque', string='Cheque Format', required=True, domain="[('journal_id', '=', journal_id)]")

    def print_dynamic_cheque_report(self):
        """
        Initiates the printing process for the dynamic cheque report.

        This method is responsible for preparing the cheque report by first creating a custom paper format
        based on the cheque configuration. Although the method for converting the amount into words and setting
        it on the cheque format is available (_amount_in_word_line), it is currently not invoked here.
        After setting up the paper format, it triggers the report action to generate and display the cheque report.

        Returns:
            dict: An action dictionary that instructs the Odoo framework to open the report in the client's browser.
        """
        self._create_paper_format()
        return self.env.ref('generate_dynamic_cheque_app.dynamic_cheque_print_report_action').report_action(self)

    @api.model
    def _create_paper_format(self):
        """
        This method creates a custom paper format for the dynamic cheque report.

        It first searches for the report action with the specified report name.
        If the report action is not found, it raises a warning indicating that the reference view of the report has been deleted.
        Then, it searches for the configuration record of the dynamic cheque.
        If no configuration record is found, it raises a warning indicating that the report format is not found.

        After obtaining the necessary configuration details, it creates a new custom paper format with the specified dimensions, margins, DPI, and orientation.
        It deletes any existing custom paper formats before creating a new one.
        Finally, it updates the paper format of the report action to the newly created custom paper format.

        Returns:
            bool: Always returns True after successfully creating the custom paper format.
        """
        report_action_id = self.env['ir.actions.report'].sudo().search(
            [('report_name', '=', 'generate_dynamic_cheque_app.report_dynamic_check_print')])
        if not report_action_id:
            raise Warning('Someone has deleted the reference view of report, Please Update the module!')
        config_rec = self.env['dynamic.cheque'].sudo().search([], limit=1)
        if not config_rec:
            raise Warning(_("Report format not found! Please Update Module."))
        page_height = config_rec.cheque_height or 10
        page_width = config_rec.cheque_width or 10
        margin_top = 0
        margin_bottom = 0
        margin_left = 0
        margin_right = 0
        dpi = 90
        header_spacing = 0
        orientation = 'Landscape'
        self._cr.execute(""" DELETE FROM report_paperformat WHERE custom_report=TRUE""")
        paperformat_id = self.env['report.paperformat'].sudo().create({
            'name': 'Custom Report',
            'format': 'A4',
            # 'page_height': page_height,
            # 'page_width': page_width,
            'dpi': dpi,
            'custom_report': True,
            'margin_top': margin_top,
            'margin_bottom': margin_bottom,
            'margin_left': margin_left,
            'margin_right': margin_right,
            'header_spacing': header_spacing,
            'orientation': orientation,
        })
        # paperformat_id = self.env['report.paperformat'].sudo().search([('name', 'ilike', 'Check Treaty Printing')], limit=1)
        report_action_id.sudo().write({'paperformat_id': paperformat_id.id})
        return True

    @api.model
    def _amount_in_word_line(self):
        """
        This method calculates and sets the amount in words for the first and second lines of the cheque.

        Parameters:
        self (PrintChequeWizard): The instance of the PrintChequeWizard model.

        Returns:
        None. The method modifies the fields of the cheque format record directly.
        """
        payment_id = self.env['account.payment'].browse(self._context.get('active_id'))
        partner = payment_id.partner_id.name_get()
        partner_id = payment_id.partner_id.display_name
        self.cheque_format.partner_id = partner_id
        amount_word = payment_id.check_amount_in_words
        first_line = (amount_word[0:self.cheque_format.words_in_fl_line])
        self.cheque_format.first_line_amount = first_line
        s1 = self.cheque_format.words_in_fl_line
        s2 = self.cheque_format.words_in_fl_line + self.cheque_format.words_in_sc_line
        second_line = (amount_word[s1:s2])
        self.cheque_format.second_line_amount = second_line
