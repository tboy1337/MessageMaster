"""
Twilio SMS service implementation
"""
import os
from typing import Dict, Any, Type, Optional

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from src.api.sms_service import SMSService, SMSResponse
from src.utils.logger import get_logger

class TwilioService(SMSService):
    """Twilio SMS service implementation"""
    
    def __init__(self):
        """Initialize the Twilio service"""
        super().__init__("Twilio", daily_limit=100)  # Default daily limit for free tier
        self.logger = get_logger()
        self.client = None
        self.from_number = None
        self.account_sid = None
        self.auth_token = None
        
        # Try to load credentials from environment variables
        self._load_env_credentials()
    
    def _load_env_credentials(self):
        """Load credentials from environment variables"""
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_number = os.environ.get("TWILIO_PHONE_NUMBER")
        
        if account_sid and auth_token and from_number:
            self.configure({
                "account_sid": account_sid,
                "auth_token": auth_token,
                "from_number": from_number
            })
    
    def configure(self, credentials: Dict[str, str]) -> bool:
        """
        Configure the Twilio service with credentials
        
        Args:
            credentials: Dictionary with account_sid, auth_token, and from_number
            
        Returns:
            True if configured successfully, False otherwise
        """
        try:
            self.account_sid = credentials.get("account_sid")
            self.auth_token = credentials.get("auth_token")
            self.from_number = credentials.get("from_number")
            
            if not all([self.account_sid, self.auth_token, self.from_number]):
                self.logger.error("Missing required Twilio credentials")
                return False
            
            # Create Twilio client
            self.client = Client(self.account_sid, self.auth_token)
            
            # Validate credentials
            if not self.validate_credentials():
                self.logger.error("Invalid Twilio credentials")
                return False
            
            self.logger.info("Twilio service configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring Twilio: {e}")
            return False
    
    def send_sms(self, recipient: str, message: str) -> SMSResponse:
        """
        Send an SMS message using Twilio
        
        Args:
            recipient: Recipient phone number (E.164 format)
            message: Message content
            
        Returns:
            SMSResponse with the result
        """
        if not self.client:
            return SMSResponse(
                success=False,
                error="Twilio service not configured"
            )
        
        try:
            # Send the message
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=recipient
            )
            
            # Return success response
            return SMSResponse(
                success=True,
                message_id=twilio_message.sid,
                details={
                    "status": getattr(twilio_message, 'status', 'sent'),
                    "price": getattr(twilio_message, 'price', '0.00'),
                    "price_unit": getattr(twilio_message, 'price_unit', 'USD'),
                    "date_created": str(getattr(twilio_message, 'date_created', ''))
                }
            )
            
        except TwilioRestException as e:
            self.logger.error(f"Twilio API error: {e}")
            error_msg = getattr(e, 'msg', 'API error')
            return SMSResponse(
                success=False,
                error=f"Twilio API error: {error_msg}",
                details={
                    "code": getattr(e, 'code', None),
                    "status": getattr(e, 'status', None)
                }
            )
        except Exception as e:
            self.logger.error(f"Error sending SMS with Twilio: {e}")
            return SMSResponse(
                success=False,
                error=f"Error: {str(e)}"
            )
    
    def check_balance(self) -> Dict[str, Any]:
        """
        Check the Twilio account balance
        
        Returns:
            Dictionary with account details
        """
        if not self.client:
            return {"error": "Twilio service not configured"}
        
        try:
            # Get account details
            account = self.client.api.accounts(self.account_sid).fetch()
            
            # Get actual balance
            balance = self.client.api.accounts(self.account_sid).balance.fetch()
            
            return {
                "balance": float(balance.balance),
                "currency": balance.currency,
                "status": getattr(account, 'status', 'active'),
                "type": getattr(account, 'type', 'standard')
            }
            
        except TwilioRestException as e:
            self.logger.error(f"Twilio API error: {e}")
            return {"error": "API error"}
        except Exception as e:
            self.logger.error(f"Error checking Twilio balance: {e}")
            return {"error": "Network error"}
    
    def get_remaining_quota(self) -> int:
        """
        Get remaining daily message quota
        
        Returns:
            Number of messages remaining in quota
        """
        # Twilio doesn't have a direct API for remaining quota
        # For free accounts, we'd need to track this in our own database
        # For paid accounts, we could check the account balance
        
        # For demonstration, return the default daily limit
        return self.daily_limit
    
    def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get delivery status for a message
        
        Args:
            message_id: Message SID to check
            
        Returns:
            Dictionary with delivery status details
        """
        if not self.client:
            return {"status": "error", "error": "Twilio service not configured"}
        
        try:
            # Get message details
            message = self.client.messages(message_id).fetch()
            
            # Return actual status
            return {
                "status": getattr(message, 'status', 'unknown'),
                "error_code": getattr(message, 'error_code', None),
                "error_message": getattr(message, 'error_message', None),
                "date_sent": str(getattr(message, 'date_sent', '')),
                "date_updated": str(getattr(message, 'date_updated', ''))
            }
            
        except TwilioRestException as e:
            self.logger.error(f"Error checking message status: {e}")
            return {"status": "error", "error": "API error"}
        except Exception as e:
            self.logger.error(f"Error checking message status: {e}")
            return {"status": "error", "error": "Network error"}
    
    def validate_credentials(self) -> bool:
        """
        Validate that the Twilio credentials are correct
        
        Returns:
            True if credentials are valid, False otherwise
        """
        if not self.client:
            return False
        
        try:
            # Try to fetch account details
            self.client.api.accounts(self.account_sid).fetch()
            return True
            
        except Exception as e:
            # Use a single catch-all exception handler for all error types
            if isinstance(e, TwilioRestException):
                self.logger.error(f"Twilio authentication error: {e}")
            else:
                self.logger.error(f"Error validating Twilio credentials: {e}")
            return False 