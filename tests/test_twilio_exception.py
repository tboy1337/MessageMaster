#!/usr/bin/env python3
"""
Test script for Twilio exception handling
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import application modules
from src.api.twilio_service import TwilioService
from src.api.sms_service import SMSResponse

class TestTwilioExceptionHandling(unittest.TestCase):
    """Test case for Twilio exception handling"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock the TwilioRestException
        self.twilio_exception_patcher = patch('src.api.twilio_service.TwilioRestException')
        self.mock_twilio_exception = self.twilio_exception_patcher.start()
        
        # Create a mock instance
        self.mock_twilio_exception_instance = MagicMock()
        self.mock_twilio_exception_instance.msg = "Test error"
        self.mock_twilio_exception_instance.code = 12345
        self.mock_twilio_exception_instance.status = 400
        self.mock_twilio_exception_instance.more_info = "https://www.twilio.com/docs/errors/12345"
        
        # Configure the mock to return our instance
        self.mock_twilio_exception.return_value = self.mock_twilio_exception_instance
        
        # Mock the Client class
        self.client_patcher = patch('twilio.rest.Client')
        self.mock_client_class = self.client_patcher.start()
        
        # Create a mock client
        self.mock_client = MagicMock()
        self.mock_client_class.return_value = self.mock_client
        
        # Create service
        self.service = TwilioService()
        
        # Configure service
        self.service.account_sid = "AC123"
        self.service.auth_token = "token123"
        self.service.from_number = "+15551234567"
        self.service.client = self.mock_client
    
    def tearDown(self):
        """Clean up test environment"""
        self.twilio_exception_patcher.stop()
        self.client_patcher.stop()
    
    def test_send_sms_twilio_exception(self):
        """Test handling of TwilioRestException when sending SMS"""
        # Set up the messages.create method to raise the exception
        self.mock_client.messages.create.side_effect = self.mock_twilio_exception_instance
        
        # Send SMS
        response = self.service.send_sms("+12125551234", "Test message")
        
        # Verify error response
        self.assertFalse(response.success)
        self.assertIn("Twilio API error", response.error)
        self.assertEqual(response.details["code"], 12345)
        self.assertEqual(response.details["status"], 400)
        self.assertEqual(response.details["more_info"], "https://www.twilio.com/docs/errors/12345")
    
    def test_check_balance_twilio_exception(self):
        """Test handling of TwilioRestException when checking balance"""
        # Set up the accounts().fetch() method to raise the exception
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.side_effect = self.mock_twilio_exception_instance
        self.mock_client.api.accounts.return_value = mock_account_callable
        
        # Check balance
        balance = self.service.check_balance()
        
        # Verify error response
        self.assertIn("error", balance)
        self.assertEqual(balance["error"], "Test error")
    
    def test_get_delivery_status_twilio_exception(self):
        """Test handling of TwilioRestException when getting delivery status"""
        # Update the mock for this test
        self.mock_twilio_exception_instance.msg = "Message not found"
        
        # Set up the messages().fetch() method to raise the exception
        mock_message_callable = MagicMock()
        mock_message_callable.fetch.side_effect = self.mock_twilio_exception_instance
        self.mock_client.messages.return_value = mock_message_callable
        
        # Get status
        status = self.service.get_delivery_status("SM123")
        
        # Verify error response
        self.assertEqual(status["status"], "error")
        self.assertEqual(status["error"], "Message not found")
    
    def test_validate_credentials_twilio_exception(self):
        """Test TwilioRestException handling in validate_credentials"""
        # Set up the accounts().fetch() method to raise the exception
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.side_effect = self.mock_twilio_exception_instance
        self.mock_client.api.accounts.return_value = mock_account_callable
        
        # Validate credentials
        result = self.service.validate_credentials()
        
        # Verify result
        self.assertFalse(result)
    
    def test_validate_credentials_general_exception(self):
        """Test general exception handling in validate_credentials"""
        # Set up the accounts().fetch() method to raise a general exception
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.side_effect = Exception("Network error")
        self.mock_client.api.accounts.return_value = mock_account_callable
        
        # Validate credentials
        result = self.service.validate_credentials()
        
        # Verify result
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main() 