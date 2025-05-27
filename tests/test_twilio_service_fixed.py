#!/usr/bin/env python3
"""
Test script for Twilio SMS service with better coverage using effective mocking
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Create the mock exception class before importing
class MockTwilioException(Exception):
    """Mock for TwilioRestException"""
    def __init__(self, status=400, code=21211, msg="Error message", more_info=None):
        self.status = status
        self.code = code
        self.msg = msg
        self.more_info = more_info or "https://www.twilio.com/docs/errors/21211"
        super().__init__(self.msg)

# Now import application modules
with patch('twilio.base.exceptions.TwilioRestException', MockTwilioException):
    from src.api.twilio_service import TwilioService
    from src.api.sms_service import SMSResponse

# Define mocks for Twilio objects
class MockTwilioMessage:
    """Mock for Twilio message object"""
    def __init__(self):
        self.sid = "SM123"
        self.status = "sent"
        self.price = "0.0075"
        self.price_unit = "USD"
        self.date_created = "2023-07-01 12:30:00"
        self.error_code = None
        self.error_message = None
        self.date_sent = "2023-07-01 12:30:45"
        self.date_updated = "2023-07-01 12:31:00"

class MockTwilioAccount:
    """Mock for Twilio account object"""
    def __init__(self):
        self.balance = 100.50
        self.status = "active"
        self.type = "trial"

class TestTwilioServiceCoverage(unittest.TestCase):
    """Test case for Twilio Service with improved coverage"""
    
    def setUp(self):
        """Set up test environment"""
        # Create patch for the Twilio client
        self.client_patcher = patch('twilio.rest.Client')
        
        # Create patch for TwilioRestException
        self.exception_patcher = patch('twilio.base.exceptions.TwilioRestException', MockTwilioException)
        self.module_exception_patcher = patch('src.api.twilio_service.TwilioRestException', MockTwilioException)
        
        # Start patches
        self.mock_client_class = self.client_patcher.start()
        self.mock_exception_class = self.exception_patcher.start()
        self.mock_module_exception = self.module_exception_patcher.start()
        
        # Create mock client
        self.mock_client = MagicMock()
        self.mock_client_class.return_value = self.mock_client
        
        # Set up credentials
        self.credentials = {
            "account_sid": "AC123",
            "auth_token": "token123",
            "from_number": "+15551234567"
        }
        
        # Create service
        self.service = TwilioService()
    
    def tearDown(self):
        """Clean up test environment"""
        self.client_patcher.stop()
        self.exception_patcher.stop()
        self.module_exception_patcher.stop()
    
    def test_send_sms_twilio_exception(self):
        """Test handling of TwilioRestException when sending SMS"""
        # Configure service first
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Create a TwilioRestException
        twilio_exception = MockTwilioException(
            status=400,
            code=21211,
            msg="Invalid phone number",
            more_info="https://www.twilio.com/docs/errors/21211"
        )
        
        # Set up the messages.create method to raise the exception
        self.mock_client.messages.create.side_effect = twilio_exception
        
        # Send SMS
        response = self.service.send_sms("+12125551234", "Test message")
        
        # Verify error response
        self.assertFalse(response.success)
        self.assertIn("Twilio API error", response.error)
        self.assertEqual(response.details["code"], 21211)
        self.assertEqual(response.details["status"], 400)
        self.assertEqual(response.details["more_info"], "https://www.twilio.com/docs/errors/21211")
    
    def test_check_balance_twilio_exception(self):
        """Test handling of TwilioRestException when checking balance"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Create a TwilioRestException
        twilio_exception = MockTwilioException(
            status=401,
            code=20003,
            msg="Authentication error"
        )
        
        # Set up the accounts().fetch() method to raise the exception
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.side_effect = twilio_exception
        self.mock_client.api.accounts.return_value = mock_account_callable
        
        # Check balance
        balance = self.service.check_balance()
        
        # Verify error response
        self.assertIn("error", balance)
        self.assertEqual(balance["error"], "Authentication error")
    
    def test_get_delivery_status_twilio_exception(self):
        """Test handling of TwilioRestException when getting delivery status"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Create a TwilioRestException
        twilio_exception = MockTwilioException(
            status=404,
            code=20404,
            msg="Message not found"
        )
        
        # Set up the messages().fetch() method to raise the exception
        mock_message_callable = MagicMock()
        mock_message_callable.fetch.side_effect = twilio_exception
        self.mock_client.messages.return_value = mock_message_callable
        
        # Get status
        status = self.service.get_delivery_status("SM123")
        
        # Verify error response
        self.assertEqual(status["status"], "error")
        self.assertEqual(status["error"], "Message not found")
    
    def test_validate_credentials_twilio_exception(self):
        """Test TwilioRestException handling in validate_credentials"""
        # Configure service (but don't use validate_credentials patch)
        self.service.account_sid = "AC123"
        self.service.auth_token = "token123"
        self.service.from_number = "+15551234567"
        self.service.client = self.mock_client
        
        # Create a TwilioRestException
        twilio_exception = MockTwilioException(
            status=401,
            code=20003,
            msg="Authentication error"
        )
        
        # Set up the accounts().fetch() method to raise the exception
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.side_effect = twilio_exception
        self.mock_client.api.accounts.return_value = mock_account_callable
        
        # Validate credentials
        result = self.service.validate_credentials()
        
        # Verify result
        self.assertFalse(result)
    
    def test_validate_credentials_general_exception(self):
        """Test general exception handling in validate_credentials"""
        # Configure service (but don't use validate_credentials patch)
        self.service.account_sid = "AC123"
        self.service.auth_token = "token123"
        self.service.from_number = "+15551234567"
        self.service.client = self.mock_client
        
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