"""
MTN USSD Integration Module

This module handles integration with MTN's USSD API for Ghana.
MTN USSD provides interactive menu-based services for mobile users.
"""

import requests
import base64
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from ..config import settings

logger = logging.getLogger(__name__)


class MTNUSSDIntegration:
    """
    Integration with MTN USSD API.
    
    MTN USSD allows applications to create interactive menus that users
    can access by dialing a shortcode (e.g., *920*55#).
    """
    
    def __init__(self):
        self.consumer_key = settings.MTN_CONSUMER_KEY
        self.consumer_secret = settings.MTN_CONSUMER_SECRET
        self.base_url = settings.MTN_BASE_URL
        self.environment = settings.MTN_ENVIRONMENT
        self.service_code = settings.MTN_USSD_SERVICE_CODE
        self.callback_url = settings.MTN_CALLBACK_URL
        self.enabled = settings.ENABLE_MTN_USSD and settings.USE_MTN_SERVICES
        
        # Token caching
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
        logger.info(f"MTN USSD Integration initialized - Environment: {self.environment}")
    
    def _get_access_token(self) -> str:
        """
        Get OAuth access token for MTN API authentication.
        Tokens are cached and refreshed when expired.
        
        Returns:
            Access token string
            
        Raises:
            Exception: If token request fails
        """
        # Return cached token if still valid
        if self._access_token and self._token_expires_at:
            if datetime.utcnow() < self._token_expires_at:
                return self._access_token
        
        # Request new token
        url = f"{self.base_url}/oauth/token"
        
        # Create Basic Auth header
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data.get("access_token")
            
            # Set expiration (usually 3600 seconds, we set it to 50 minutes to be safe)
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 600)
            
            logger.info("Successfully obtained MTN access token")
            return self._access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to obtain MTN access token: {e}")
            raise Exception(f"MTN authentication failed: {e}")
    
    def send_ussd_message(
        self,
        session_id: str,
        phone_number: str,
        message: str,
        is_final: bool = False
    ) -> Dict:
        """
        Send USSD message to user.
        
        Args:
            session_id: USSD session ID
            phone_number: User's phone number (with country code)
            message: Message to display to user
            is_final: Whether this is the final message (ends session)
            
        Returns:
            Response from MTN API
            
        Raises:
            Exception: If API request fails
        """
        if not self.enabled:
            logger.warning("MTN USSD is disabled")
            return {"status": "disabled", "message": "MTN USSD is not enabled"}
        
        access_token = self._get_access_token()
        
        url = f"{self.base_url}/ussd/send"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "sessionId": session_id,
            "phoneNumber": phone_number,
            "message": message,
            "type": "END" if is_final else "CON",
            "serviceCode": self.service_code
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"USSD message sent to {phone_number}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send USSD message: {e}")
            raise Exception(f"Failed to send USSD message: {e}")
    
    def format_response(self, message: str, is_final: bool = False) -> str:
        """
        Format USSD response according to MTN requirements.
        
        MTN USSD responses should be prefixed with:
        - "CON " for continuation (waiting for user input)
        - "END " for final messages (session end)
        
        Args:
            message: The message content
            is_final: Whether this is the final message
            
        Returns:
            Formatted USSD response string
        """
        prefix = "END" if is_final else "CON"
        return f"{prefix} {message}"
    
    def validate_request(self, request_data: Dict) -> bool:
        """
        Validate incoming USSD request from MTN.
        
        Args:
            request_data: Request data from MTN
            
        Returns:
            True if request is valid
        """
        required_fields = ["sessionId", "phoneNumber", "serviceCode"]
        
        for field in required_fields:
            if field not in request_data:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate service code matches
        if request_data.get("serviceCode") != self.service_code:
            logger.warning(f"Invalid service code: {request_data.get('serviceCode')}")
            return False
        
        return True
    
    def parse_user_input(self, text: str) -> list:
        """
        Parse user input from USSD request.
        
        MTN sends user input as a string with asterisks (*) separating menu choices.
        For example: "1*2*3" means user selected 1, then 2, then 3.
        
        Args:
            text: Raw text from USSD request
            
        Returns:
            List of user inputs
        """
        if not text or text == "":
            return []
        
        return text.split("*")
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get information about a USSD session.
        
        Args:
            session_id: USSD session ID
            
        Returns:
            Session information or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            access_token = self._get_access_token()
            
            url = f"{self.base_url}/ussd/sessions/{session_id}"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get session info: {e}")
            return None
    
    def end_session(self, session_id: str, message: str = "Thank you!") -> str:
        """
        End a USSD session with a final message.
        
        Args:
            session_id: USSD session ID
            message: Final message to display
            
        Returns:
            Formatted END response
        """
        return self.format_response(message, is_final=True)
    
    def continue_session(self, message: str) -> str:
        """
        Continue a USSD session with a message and wait for input.
        
        Args:
            message: Message to display
            
        Returns:
            Formatted CON response
        """
        return self.format_response(message, is_final=False)


# Singleton instance
mtn_ussd_service = MTNUSSDIntegration()

