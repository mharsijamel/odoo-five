# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class DynamicChequeGenerate(models.AbstractModel):
	_name = 'report.generate_dynamic_cheque_app.report_dynamic_check_print'

	def get_amount_in_word_line(self, payment_id, cheque_format):
		"""
		Converts the payment amount into words and splits it into two lines based on the cheque format.

		This method takes a payment record and a cheque format record, converts the payment amount into words,
		and then splits this string into two parts to fit the format specified for the first and second lines
		on the cheque. This is particularly useful for printing cheques where the amount in words needs to
		be formatted across multiple lines.

		Parameters:
		- payment_id: Record of the payment for which the amount in words is needed. It should have a currency_id
		  and an amount field.
		- cheque_format: Record specifying the cheque format. It must have words_in_fl_line and words_in_sc_line
		  fields indicating how many characters can fit in the first and second lines of the cheque, respectively.

		Returns:
		- A dictionary with two keys, 'first_line' and 'second_line', containing the split amount in words.
		"""

		amount_word = payment_id.currency_id.amount_to_text(payment_id.amount)
		first_line = (amount_word[0:cheque_format.words_in_fl_line])
		s1 = cheque_format.words_in_fl_line
		s2 = cheque_format.words_in_fl_line + cheque_format.words_in_sc_line
		second_line = (amount_word[s1:s2])
		localdict = {
			'first_line': first_line,
			'second_line': second_line
		}
		return localdict

	def _get_report_values(self, docids, data=None):
		"""
		Prepares the data required for rendering the cheque report.

		This method fetches the cheque wizard record using the provided document IDs, then constructs a dictionary
		containing the model name, cheque format, payment record, and a method to split the payment amount into words
		formatted for the cheque. This dictionary is used in the report template to display the cheque information.

		Parameters:
		- docids: List of document IDs for which the report is being generated. Expected to correspond to
		          'dynamic.cheque.wizard' records.
		- data: Optional dictionary containing any additional data. This is not used in the current implementation
		        but is available for future extensions or customizations.

		Returns:
		- A dictionary with keys 'doc_model', 'cheque_format', 'payment_id', and 'get_amount_in_word_line', which
		  are used in the report template to render the cheque details.
		"""
		wizard = self.env['dynamic.cheque.wizard'].browse(docids)
		return {
			'doc_model': 'dynamic.cheque',
			'cheque_format': wizard.cheque_format,
			'payment_id': wizard.payment_id,
			'get_amount_in_word_line': self.get_amount_in_word_line,
		}


class ReportPaperFormat(models.Model):
	_inherit = "report.paperformat"

	custom_report = fields.Boolean('Temp Formats', default=False)
