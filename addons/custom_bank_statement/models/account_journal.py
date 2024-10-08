from odoo import models, api
import logging

# Define the logger
_logger = logging.getLogger(__name__)
import ast
class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def action_outstanding_payments(self):
        ''' Show the bank balance inside the General Ledger report filtered by default_account_id. '''
        self.ensure_one()

        # Action to open journal items with domain filtering by journal_id and reconciled=False
        action = self.env.ref('custom_bank_statement.action_open_journal_items_with_bank_balance').read()[0]
        
        # Add dynamic domain to filter journal_id based on default_account_id and unreconciled lines

        action['domain'] = [
            ('account_id', '=', self.suspense_account_id.id),
            ('journal_id', '=', self.id),
            ('reconciled', '=', False)
        ]
        #action['context'] = dict(ast.literal_eval(action['context']), journal_id=self.default_account_id)
        # Set the context for additional filters
        action['context'] = dict(self.env.context, search_default_posted=1)
        
        return action
