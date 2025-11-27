#!/usr/bin/env python3
"""
Test script for AfricaTalking USSD integration.
This simulates how AfricaTalking sends USSD requests to your callback endpoint.

Usage:
    python test_africastalking_ussd.py
"""

import requests
import uuid
from typing import Optional


class USSDSimulator:
    """Simulates AfricaTalking USSD requests for local testing."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.callback_url = f"{base_url}/ussd/callback"
        self.session_id = str(uuid.uuid4())
        self.phone_number = "+256700000001"  # Test phone number
        self.service_code = "*384*12345#"
        self.text = ""
        
    def send_request(self, user_input: Optional[str] = None) -> str:
        """
        Send a USSD request to the callback endpoint.
        
        Args:
            user_input: User's input (None for initial request)
            
        Returns:
            Response from the USSD service
        """
        # Update text based on user input
        if user_input is not None:
            if self.text:
                self.text += f"*{user_input}"
            else:
                self.text = user_input
        
        # Prepare form data as AfricaTalking sends it
        data = {
            "sessionId": self.session_id,
            "serviceCode": self.service_code,
            "phoneNumber": self.phone_number,
            "text": self.text
        }
        
        # Send POST request
        response = requests.post(self.callback_url, data=data)
        
        if response.status_code == 200:
            return response.text
        else:
            return f"Error {response.status_code}: {response.text}"
    
    def reset_session(self):
        """Start a new USSD session."""
        self.session_id = str(uuid.uuid4())
        self.text = ""
    
    def interactive_session(self):
        """Run an interactive USSD session."""
        print("=" * 60)
        print("AfricaTalking USSD Simulator")
        print("=" * 60)
        print(f"Phone Number: {self.phone_number}")
        print(f"Service Code: {self.service_code}")
        print(f"Session ID: {self.session_id}")
        print("=" * 60)
        
        # Initial request
        response = self.send_request()
        print(f"\n{response}\n")
        
        # Continue until session ends
        while response.startswith("CON"):
            user_input = input("Enter your choice: ").strip()
            
            if user_input.lower() == 'quit':
                print("Session terminated by user.")
                break
            
            response = self.send_request(user_input)
            print(f"\n{response}\n")
        
        print("=" * 60)
        print("Session ended.")
        print("=" * 60)


def run_automated_tests():
    """Run automated test scenarios."""
    print("\n" + "=" * 60)
    print("Running Automated USSD Tests")
    print("=" * 60)
    
    # Test 1: Main Menu
    print("\nTest 1: Display Main Menu")
    sim = USSDSimulator()
    response = sim.send_request()
    assert "CON" in response, "Should show continue menu"
    assert "SusuSave" in response, "Should show app name"
    print("✓ Main menu displayed correctly")
    
    # Test 2: Check Status (Option 3)
    print("\nTest 2: Check Status (Empty Groups)")
    sim.reset_session()
    sim.send_request()  # Initial request
    response = sim.send_request("3")  # Select option 3
    assert "END" in response, "Should end session"
    print("✓ Status check works")
    
    # Test 3: Invalid Option
    print("\nTest 3: Invalid Menu Option")
    sim.reset_session()
    sim.send_request()  # Initial request
    response = sim.send_request("9")  # Invalid option
    assert "END" in response, "Should end session"
    assert "Invalid" in response, "Should show error message"
    print("✓ Invalid option handled correctly")
    
    # Test 4: Join Group Flow
    print("\nTest 4: Join Group (Enter Code)")
    sim.reset_session()
    sim.send_request()  # Initial request
    response = sim.send_request("1")  # Select option 1 (Join Group)
    assert "CON" in response, "Should ask for group code"
    assert "Group Code" in response, "Should mention group code"
    print("✓ Join group flow initiated")
    
    print("\n" + "=" * 60)
    print("All automated tests passed!")
    print("=" * 60)


def main():
    """Main function."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run automated tests
        run_automated_tests()
    else:
        # Run interactive session
        sim = USSDSimulator()
        sim.interactive_session()


if __name__ == "__main__":
    main()

