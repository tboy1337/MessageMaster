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

class MockTwilioException(Exception):
    """Mock exception for testing"""
    pass

class TestTwilioExceptionHandling(unittest.TestCase):
    """Test case for Twilio exception handling"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a custom exception that's already a subclass of Exception
        self.mock_exception = MockTwilioException("Test error")
        self.mock_exception.code = 12345
        self.mock_exception.status = 400
        
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
        self.client_patcher.stop()
    
    def test_send_sms_twilio_exception(self):
        """Test handling of TwilioRestException when sending SMS"""
        # Set up the messages.create method to raise the exception
        self.mock_client.messages.create.side_effect = self.mock_exception
        
        # Send SMS
        response = self.service.send_sms("+12125551234", "Test message")
        
        # Verify error response
        self.assertFalse(response.success)
        self.assertIn("Error:", response.error)
    
    def test_check_balance_twilio_exception(self):
        """Test handling of TwilioRestException when checking balance"""
        # Set up the accounts().fetch() method to raise the exception
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.side_effect = self.mock_exception
        self.mock_client.api.accounts.return_value = mock_account_callable
        
        # Check balance
        balance = self.service.check_balance()
        
        # Verify error response
        self.assertIn("error", balance)
    
    def test_get_delivery_status_twilio_exception(self):
        """Test handling of TwilioRestException when getting delivery status"""
        # Set up the messages().fetch() method to raise the exception
        mock_message_callable = MagicMock()
        mock_message_callable.fetch.side_effect = self.mock_exception
        self.mock_client.messages.return_value = mock_message_callable
        
        # Get status
        status = self.service.get_delivery_status("SM123")
        
        # Verify error response
        self.assertEqual(status["status"], "error")
    
    def test_validate_credentials_twilio_exception(self):
        """Test TwilioRestException handling in validate_credentials"""
        # Set up the accounts().fetch() method to raise the exception
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.side_effect = self.mock_exception
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