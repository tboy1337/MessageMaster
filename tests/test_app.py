#!/usr/bin/env python3
"""
Test script for MessageMaster application
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import tempfile
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application modules
from src.models.database import Database
from src.api.service_manager import SMSServiceManager
from src.models.contact_manager import ContactManager
from src.api.sms_service import SMSResponse
from src.services.config_service import ConfigService

class TestSMSApp(unittest.TestCase):
    """Test case for SMS application"""
    
    def setUp(self):
        """Set up test environment"""
        # Create mock database
        self.db = MagicMock(spec=Database)
        self.db.get_api_credentials.return_value = None
        self.db.get_active_services.return_value = []
        
        # Create a temporary directory for config files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Patch the home directory to use our temp directory
        self.home_patcher = patch('pathlib.Path.home', return_value=Path(self.temp_dir.name))
        self.mock_home = self.home_patcher.start()
        
        # Create config service with temporary config directory
        self.config = ConfigService("test_app")
        
        # Create notification service mock
        self.notification = MagicMock()
    
    def tearDown(self):
        """Clean up test environment"""
        # Stop the patchers
        self.home_patcher.stop()
        
        # Clean up temp directory
        self.temp_dir.cleanup()
    
    def test_service_manager(self):
        """Test SMS service manager"""
        # Create manager with mock database
        manager = SMSServiceManager(self.db)
        
        # Verify available services
        services = manager.get_available_services()
        self.assertIsInstance(services, list)
        self.assertTrue('twilio' in services)
        self.assertTrue('textbelt' in services)
        
        # Test get service by name
        twilio = manager.get_service_by_name('twilio')
        self.assertIsNotNone(twilio)
        self.assertEqual(twilio.service_name, 'Twilio')
        
        textbelt = manager.get_service_by_name('textbelt')
        self.assertIsNotNone(textbelt)
        self.assertEqual(textbelt.service_name, 'TextBelt')
    
    def test_contact_manager(self):
        """Test contact manager"""
        # Set up mock for database
        self.db.get_contacts.return_value = []
        self.db.save_contact.return_value = True
        
        # Create manager with mock database
        manager = ContactManager(self.db)
        
        # Test getting contacts
        contacts = manager.get_all_contacts()
        self.assertIsInstance(contacts, list)
        
        # Mock validation method to return success
        with patch('src.models.contact_manager.ContactManager._validate_phone_number',
                  return_value=(True, '+12125551234')):
            # Test adding contact
            result = manager.add_contact("Test User", "12125551234", "US", "Test note")
            self.assertTrue(result)
            self.db.save_contact.assert_called_once()
    
    def test_config_service(self):
        """Test config service"""
        # Test default settings
        self.assertIsNotNone(self.config.get("general.start_minimized"))
        self.assertFalse(self.config.get("general.start_minimized"))
        
        # Test setting a value
        self.config.set("general.start_minimized", True)
        self.assertTrue(self.config.get("general.start_minimized"))
        
        # Test non-existent key with default
        self.assertEqual(self.config.get("nonexistent.key", "default"), "default")
        
        # Test nested setting
        self.config.set("test.nested.setting", 123)
        self.assertEqual(self.config.get("test.nested.setting"), 123)
    
    def test_sms_response(self):
        """Test SMS response object"""
        # Create success response
        success = SMSResponse(
            success=True,
            message_id="msg123",
            details={"status": "sent"}
        )
        self.assertTrue(success.success)
        self.assertEqual(success.message_id, "msg123")
        self.assertIn("status", success.details)
        
        # Create error response
        error = SMSResponse(
            success=False,
            error="Connection failed",
            details={"code": 500}
        )
        self.assertFalse(error.success)
        self.assertEqual(error.error, "Connection failed")
        self.assertIn("code", error.details)
        self.assertEqual(error.details["code"], 500)
        
        # Test string representation
        self.assertIn("Success", str(success))
        self.assertIn("Failed", str(error))

    @unittest.skip("Requires GUI environment")
    def test_app_initialization(self):
        """Test basic application initialization"""
        # This test requires a GUI environment
        from src.gui.app import SMSApplication
        
        # Initialize Tk
        root = tk.Tk()
        
        # Create application
        app = SMSApplication(root, config=self.config, notification=self.notification)
        
        # Verify application components
        self.assertIsNotNone(app.db)
        self.assertIsNotNone(app.service_manager)
        self.assertIsNotNone(app.contact_manager)
        self.assertIsNotNone(app.scheduler)
        
        # Clean up
        root.destroy()

if __name__ == "__main__":
    unittest.main() 