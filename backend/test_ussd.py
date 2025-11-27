#!/usr/bin/env python3
"""
USSD Simulator for testing Africa's Talking webhook locally.
Simulates POST requests to the /ussd/callback endpoint.
"""

import requests
import uuid
from typing import Optional


class USSDSimulator:
    """Simulate USSD interactions with the backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = str(uuid.uuid4())
        self.text = ""
    
    def dial(self, phone_number: str, ussd_code: str = "*920*55#"):
        """
        Initiate a USSD session.
        
        Args:
            phone_number: User's phone number (e.g., +233244123456)
            ussd_code: USSD code to dial
        """
        print(f"\n📞 Dialing {ussd_code} from {phone_number}...")
        self.session_id = str(uuid.uuid4())
        self.text = ""
        
        response = self._send_request(phone_number, self.text)
        print(f"\n{response}")
        
        return response
    
    def send_input(self, phone_number: str, user_input: str):
        """
        Send user input to continue the USSD session.
        
        Args:
            phone_number: User's phone number
            user_input: User's input (e.g., "1" for menu option 1)
        """
        if self.text:
            self.text += f"*{user_input}"
        else:
            self.text = user_input
        
        print(f"\n➡️ User input: {user_input}")
        response = self._send_request(phone_number, self.text)
        print(f"\n{response}")
        
        # Check if session ended
        if response.startswith("END"):
            print("\n🔚 Session ended")
            self.reset()
        
        return response
    
    def _send_request(self, phone_number: str, text: str) -> str:
        """Send request to USSD callback endpoint."""
        url = f"{self.base_url}/ussd/callback"
        
        data = {
            "sessionId": self.session_id,
            "phoneNumber": phone_number,
            "text": text
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.text
        
        except requests.exceptions.RequestException as e:
            return f"ERROR: {str(e)}"
    
    def reset(self):
        """Reset the session."""
        self.session_id = str(uuid.uuid4())
        self.text = ""


def main():
    """Interactive USSD testing."""
    print("=" * 60)
    print("   SusuSave USSD Simulator")
    print("=" * 60)
    
    simulator = USSDSimulator()
    
    # Get phone number
    phone = input("\nEnter phone number (e.g., +233244123456): ").strip()
    
    if not phone:
        phone = "+233244123456"  # Default test number
        print(f"Using default: {phone}")
    
    # Start session
    response = simulator.dial(phone)
    
    # Interactive loop
    while True:
        if response.startswith("END"):
            restart = input("\nStart new session? (y/n): ").strip().lower()
            if restart == 'y':
                response = simulator.dial(phone)
                continue
            else:
                break
        
        user_input = input("\nEnter your choice: ").strip()
        
        if not user_input:
            break
        
        if user_input.lower() == 'quit':
            break
        
        response = simulator.send_input(phone, user_input)
    
    print("\n👋 Goodbye!\n")


if __name__ == "__main__":
    main()

