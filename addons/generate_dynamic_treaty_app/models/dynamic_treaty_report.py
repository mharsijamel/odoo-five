# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class DynamictreatyGenerate(models.AbstractModel):
	_name = 'report.generate_dynamic_treaty_app.report_dynamic_treaty_print'

	def get_amount_in_word_line(self, payment_id, treaty_format):
		"""
		Converts the payment amount into words and splits it into two lines based on the treaty format.

		This method takes a payment record and a treaty format record, converts the payment amount into words,
		and then splits this string into two parts to fit the format specified for the first and second lines
		on the treaty. This is particularly useful for printing treatys where the amount in words needs to
		be formatted across multiple lines.

		Parameters:
		- payment_id: Record of the payment for which the amount in words is needed. It should have a currency_id
		  and an amount field.
		- treaty_format: Record specifying the treaty format. It must have words_in_fl_line and words_in_sc_line
		  fields indicating how many characters can fit in the first and second lines of the treaty, respectively.

		Returns:
		- A dictionary with two keys, 'first_line' and 'second_line', containing the split amount in words.
		"""

		amount_word = payment_id.currency_id.amount_to_text(payment_id.amount)
		first_line = (amount_word[0:treaty_format.words_in_fl_line])
		s1 = treaty_format.words_in_fl_line
		s2 = treaty_format.words_in_fl_line + treaty_format.words_in_sc_line
		second_line = amount_word
		localdict = {
			'first_line': '',
			'second_line': second_line
		}
		return localdict

	def _get_report_values(self, docids, data=None):
		"""
		Prepares the data required for rendering the treaty report.

		This method fetches the treaty wizard record using the provided document IDs, then constructs a dictionary
		containing the model name, treaty format, payment record, and a method to split the payment amount into words
		formatted for the treaty. This dictionary is used in the report template to display the treaty information.

		Parameters:
		- docids: List of document IDs for which the report is being generated. Expected to correspond to
		          'dynamic.treaty.wizard' records.
		- data: Optional dictionary containing any additional data. This is not used in the current implementation
		        but is available for future extensions or customizations.

		Returns:
		- A dictionary with keys 'doc_model', 'treaty_format', 'payment_id', and 'get_amount_in_word_line', which
		  are used in the report template to render the treaty details.
		"""
		wizard = self.env['dynamic.treaty.wizard'].browse(docids)
		return {
			'doc_model': 'dynamic.treaty',
			'treaty_format': wizard.treaty_format,
			'payment_id': wizard.payment_id,
			'get_amount_in_word_line': self.get_amount_in_word_line,
		}

class ReportPaperFormat(models.Model):
	_inherit = "report.paperformat"

	custom_report_treaty = fields.Boolean('Temp treaty Formats', default=False)
