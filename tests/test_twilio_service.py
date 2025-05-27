#!/usr/bin/env python3
"""
Test script for Twilio SMS service with comprehensive coverage
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

class MockMessage:
    """Mock for a Twilio message object"""
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

class MockAccount:
    """Mock for a Twilio account object"""
    def __init__(self):
        self.balance = 100.50
        self.status = "active"
        self.type = "trial"

class TestTwilioServiceDetailed(unittest.TestCase):
    """Test case for Twilio Service with detailed coverage"""
    
    def setUp(self):
        """Set up test environment"""
        self.client_patcher = patch('twilio.rest.Client')
        self.mock_client_class = self.client_patcher.start()
        
        # Create a mock client
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
    
    def test_configure(self):
        """Test configuring the service"""
        # Configure with valid credentials
        with patch.object(self.service, 'validate_credentials', return_value=True):
            result = self.service.configure(self.credentials)
            self.assertTrue(result)
            self.assertEqual(self.service.account_sid, "AC123")
            self.assertEqual(self.service.auth_token, "token123")
            self.assertEqual(self.service.from_number, "+15551234567")
    
    def test_configure_missing_credentials(self):
        """Test configuring with missing credentials"""
        # Configure with incomplete credentials
        result = self.service.configure({
            "account_sid": "AC123",
            # Missing auth_token and from_number
        })
        self.assertFalse(result)
    
    def test_configure_validation_failure(self):
        """Test configuring with invalid credentials"""
        # Configure with invalid credentials
        with patch.object(self.service, 'validate_credentials', return_value=False):
            result = self.service.configure(self.credentials)
            self.assertFalse(result)
    
    def test_configure_exception(self):
        """Test exception handling in configure method"""
        # Configure with exception
        with patch('twilio.rest.Client', side_effect=Exception("Connection error")):
            result = self.service.configure(self.credentials)
            self.assertFalse(result)
    
    def test_load_env_credentials(self):
        """Test loading credentials from environment variables"""
        # Mock environment variables
        env_values = {
            "TWILIO_ACCOUNT_SID": "AC_env_test",
            "TWILIO_AUTH_TOKEN": "token_env_test",
            "TWILIO_PHONE_NUMBER": "+15551234567"
        }
        
        with patch('os.environ.get', side_effect=lambda key: env_values.get(key)):
            # Mock configure method
            with patch.object(TwilioService, 'configure', return_value=True) as mock_configure:
                # Create service
                service = TwilioService()
                
                # Verify configure was called with the right credentials
                mock_configure.assert_called_once_with({
                    "account_sid": "AC_env_test",
                    "auth_token": "token_env_test",
                    "from_number": "+15551234567"
                })
    
    def test_validate_credentials(self):
        """Test validating credentials"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Create a mock account
        mock_account = MockAccount()
        
        # Set up the accounts method
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.return_value = mock_account
        self.mock_client.api.accounts.return_value = mock_account_callable
        
        # Validate credentials
        result = self.service.validate_credentials()
        self.assertTrue(result)
        
        # Validate with exception
        mock_account_callable.fetch.side_effect = Exception("Invalid credentials")
        result = self.service.validate_credentials()
        self.assertFalse(result)
    
    def test_send_sms_unconfigured(self):
        """Test sending SMS without configuring"""
        # Create service without configuring
        service = TwilioService()
        service.client = None
        
        # Send SMS
        response = service.send_sms("+12125551234", "Test message")
        
        # Verify error response
        self.assertFalse(response.success)
        self.assertEqual(response.error, "Twilio service not configured")
    
    def test_send_sms(self):
        """Test sending SMS successfully"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Create a mock message
        mock_message = MockMessage()
        
        # Set up the messages.create method
        self.mock_client.messages.create.return_value = mock_message
        
        # Send SMS
        response = self.service.send_sms("+12125551234", "Test message")
        
        # Verify successful response
        self.assertTrue(response.success)
        self.assertEqual(response.message_id, "SM123")
        self.assertEqual(response.details["status"], "sent")
        self.assertEqual(response.details["price"], "0.0075")
    
    def test_send_sms_api_error(self):
        """Test handling of API error when sending SMS"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Mock error from Twilio API
        error = Exception("API error")
        error.msg = "Invalid phone number"
        error.code = 21211
        error.status = 400
        
        # Set up the messages.create method to raise the exception
        self.mock_client.messages.create.side_effect = error
        
        # Patch the TwilioRestException with our own implementation
        with patch('src.api.twilio_service.TwilioRestException', Exception):
            # Send SMS
            response = self.service.send_sms("+12125551234", "Test message")
            
            # Verify error response
            self.assertFalse(response.success)
            self.assertIn("Error:", response.error)
    
    def test_send_sms_general_error(self):
        """Test handling of general error when sending SMS"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Set up the messages.create method to raise a general exception
        self.mock_client.messages.create.side_effect = Exception("Network error")
        
        # Send SMS
        response = self.service.send_sms("+12125551234", "Test message")
        
        # Verify error response
        self.assertFalse(response.success)
        self.assertIn("Error:", response.error)
    
    def test_check_balance_unconfigured(self):
        """Test checking balance without configuring"""
        # Create service without configuring
        service = TwilioService()
        service.client = None
        
        # Check balance
        balance = service.check_balance()
        
        # Verify error response
        self.assertIn("error", balance)
        self.assertEqual(balance["error"], "Twilio service not configured")
    
    def test_check_balance(self):
        """Test checking balance successfully"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Create a mock account
        mock_account = MockAccount()
        
        # Set up the accounts method
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.return_value = mock_account
        self.mock_client.api.accounts.return_value = mock_account_callable
        
        # Check balance
        balance = self.service.check_balance()
        
        # Verify response
        self.assertEqual(balance["balance"], 100.50)
        self.assertEqual(balance["status"], "active")
        self.assertEqual(balance["type"], "trial")
    
    def test_check_balance_api_error(self):
        """Test handling of API error when checking balance"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Mock error from Twilio API
        error = Exception("API error")
        
        # Set up the accounts method to raise the exception
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.side_effect = error
        self.mock_client.api.accounts.return_value = mock_account_callable
        
        # Patch the TwilioRestException with our own implementation
        with patch('src.api.twilio_service.TwilioRestException', Exception):
            # Check balance
            balance = self.service.check_balance()
            
            # Verify error response
            self.assertIn("error", balance)
            self.assertEqual(balance["error"], "API error")
    
    def test_check_balance_general_error(self):
        """Test handling of general error when checking balance"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Set up the accounts method to raise a general exception
        mock_account_callable = MagicMock()
        mock_account_callable.fetch.side_effect = Exception("Network error")
        self.mock_client.api.accounts.return_value = mock_account_callable
        
        # Check balance
        balance = self.service.check_balance()
        
        # Verify error response
        self.assertIn("error", balance)
        self.assertEqual(balance["error"], "Network error")
    
    def test_get_remaining_quota(self):
        """Test getting remaining quota"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Get quota
        quota = self.service.get_remaining_quota()
        
        # Verify response
        self.assertEqual(quota, 100)  # Default daily limit for free tier
    
    def test_get_delivery_status_unconfigured(self):
        """Test getting delivery status without configuring"""
        # Create service without configuring
        service = TwilioService()
        service.client = None
        
        # Get status
        status = service.get_delivery_status("SM123")
        
        # Verify error response
        self.assertEqual(status["status"], "unknown")
        self.assertEqual(status["error"], "Twilio service not configured")
    
    def test_get_delivery_status(self):
        """Test getting delivery status successfully"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Create a mock message
        mock_message = MockMessage()
        
        # Set up the messages method
        mock_message_callable = MagicMock()
        mock_message_callable.fetch.return_value = mock_message
        self.mock_client.messages.return_value = mock_message_callable
        
        # Get status
        status = self.service.get_delivery_status("SM123")
        
        # Verify response
        self.assertEqual(status["status"], "sent")
        self.assertEqual(status["error_code"], None)
        self.assertEqual(status["error_message"], None)
    
    def test_get_delivery_status_api_error(self):
        """Test handling of API error when getting delivery status"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Mock error from Twilio API
        error = Exception("API error")
        
        # Set up the messages method to raise the exception
        mock_message_callable = MagicMock()
        mock_message_callable.fetch.side_effect = error
        self.mock_client.messages.return_value = mock_message_callable
        
        # Patch the TwilioRestException with our own implementation
        with patch('src.api.twilio_service.TwilioRestException', Exception):
            # Get status
            status = self.service.get_delivery_status("SM123")
            
            # Verify error response
            self.assertEqual(status["status"], "error")
            self.assertEqual(status["error"], "API error")
    
    def test_get_delivery_status_general_error(self):
        """Test handling of general error when getting delivery status"""
        # Configure service
        with patch.object(self.service, 'validate_credentials', return_value=True):
            self.service.configure(self.credentials)
        
        # Set up the messages method to raise a general exception
        mock_message_callable = MagicMock()
        mock_message_callable.fetch.side_effect = Exception("Network error")
        self.mock_client.messages.return_value = mock_message_callable
        
        # Get status
        status = self.service.get_delivery_status("SM123")
        
        # Verify error response
        self.assertEqual(status["status"], "error")
        self.assertEqual(status["error"], "Network error")

if __name__ == "__main__":
    unittest.main() 