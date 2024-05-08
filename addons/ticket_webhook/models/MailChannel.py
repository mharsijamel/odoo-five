from odoo import models, fields, api
import logging
import json
import requests
from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)

class MailChannel(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        message = super(MailChannel, self).create(values)
        self._log_message_data(message)
        self._send_webhook(message)
        return message

    def _log_message_data(self, message):
        # Splitting record_name to extract sender and receiver
        if isinstance(message.record_name, str):
            parts = message.record_name.split(',')
            receiver = parts[0]
        else:
            receiver = None
        
        receiver_str = "No receiver"

        if receiver:
            receiver_str = receiver

        if receiver_str.lower() == 'webvue':
            _logger.info("Message sent by %s to %s on %s: %s", message.author_id.name, receiver_str, message.date, message.body)
        
    def _send_webhook(self, message):
        # Define your webhook URL
        webhook_url = "https://webhook.site/746b10a1-41ab-49f1-96ba-dfc2a6dfd409"

        # Splitting record_name to extract sender and receiver
        if isinstance(message.record_name, str):
            parts = message.record_name.split(',')
            receiver = parts[0]
        else:
            receiver = None
        
        receiver_str = "No receiver"
        if receiver:
            receiver_str = receiver

        # Check if receiver_str is 'webvue'
        if receiver_str.lower() == 'webvue':
            # Convert date to string format
            date_string = message.date.strftime("%Y-%m-%d %H:%M:%S")
            message_body= BeautifulSoup(message.body, 'html.parser').get_text()
            # Define payload with string date and extracted sender and receiver
            payload = {
                "author": message.author_id.email,
                "receiver": receiver_str,
                "date": date_string,
                "body": message_body
            }

            try:
                # Send payload via POST request
                response = requests.post(webhook_url, json=payload)
                if response.status_code == 200:
                    _logger.info("Webhook sent successfully.")
                else:
                    _logger.error("Failed to send webhook. Status code: %s", response.status_code)
            except Exception as e:
                _logger.error("Error sending webhook: %s", e)
        else:
            _logger.info("No webhook sent as receiver is not 'webvue'.")

