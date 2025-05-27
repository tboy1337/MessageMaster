#!/usr/bin/env python3
"""
Test script specifically targeting the remaining uncovered lines in Twilio service
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

# Create a simple TwilioRestException mock for patching
class MockTwilioRestException(Exception):
    """Mock for TwilioRestException that can be used for patching"""
    def __init__(self, msg="Error", code=12345, status=400, more_info="https://docs.example.com"):
        self.msg = msg
        self.code = code
        self.status = status
        self.more_info = more_info
        super().__init__(msg)

class TestTwilioRemainingCoverage(unittest.TestCase):
    """Test case for remaining uncovered lines in Twilio Service"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock twilio.rest.Client
        self.client_patcher = patch('twilio.rest.Client')
        self.exception_patcher = patch('src.api.twilio_service.TwilioRestException', MockTwilioRestException)
        
        self.mock_client_class = self.client_patcher.start()
        self.mock_exception_class = self.exception_patcher.start()
        
        # Create service
        self.service = TwilioService()
        
        # Set up credentials
        self.credentials = {
            "account_sid": "AC123",
            "auth_token": "token123",
            "from_number": "+15551234567"
        }
        
        # Configure service with validation bypass
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
    
    def tearDown(self):
        """Clean up test environment"""
        self.client_patcher.stop()
        self.exception_patcher.stop()
    
    def test_send_sms_twilio_exception(self):
        """Test send_sms error handling for TwilioRestException"""
        # Create exception with properties we need
        twilio_exception = MockTwilioRestException(
            msg="Invalid phone number",
            code=21211,
            status=400,
            more_info="https://www.twilio.com/docs/errors/21211"
        )
        
        # Set up mock client to raise the exception
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = twilio_exception
        
        # Replace the service's client
        self.service.client = mock_client
        
        # Send SMS, which should catch the exception
        response = self.service.send_sms("+12125551234", "Test message")
        
        # Verify error response
        self.assertFalse(response.success)
        self.assertIn("Twilio API error", response.error)
        self.assertEqual(response.details["code"], 21211)
        self.assertEqual(response.details["status"], 400)
        self.assertEqual(response.details["more_info"], "https://www.twilio.com/docs/errors/21211")
    
    def test_validate_credentials_general_exception(self):
        """Test validate_credentials exception handling for general exceptions"""
        # Create a mock client
        mock_client = MagicMock()
        
        # Set up the accounts method to raise a general exception
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.side_effect = Exception("General network error")
        mock_client.api.accounts.return_value = mock_account_callable
        
        # Configure service
        service = TwilioService()
        service.client = mock_client
        service.account_sid = "AC123"
        
        # Validate credentials (should handle the exception)
        result = service.validate_credentials()
        
        # Verify result
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main() 