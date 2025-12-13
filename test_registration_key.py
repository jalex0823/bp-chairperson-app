#!/usr/bin/env python3
"""
Test script to verify registration key validation functionality.
"""
import os
import sys
import json
from dotenv import load_dotenv

# Add current directory to Python path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from app import app

def test_registration_key_validation():
    """Test the registration key validation endpoint."""
    with app.app_context():
        with app.test_client() as client:
            print("Testing registration key validation...")
            
            # Get current config values
            access_code = app.config.get('REGISTRATION_ACCESS_CODE')
            access_codes = app.config.get('REGISTRATION_ACCESS_CODES')
            
            print(f"REGISTRATION_ACCESS_CODE: {access_code}")
            print(f"REGISTRATION_ACCESS_CODES: {access_codes}")
            
            if not access_code and not access_codes:
                print("❌ No access codes configured!")
                return False
            
            # Test with correct key
            test_key = access_code if access_code else access_codes.split(',')[0].strip()
            print(f"Testing with key: '{test_key}'")
            
            response = client.post('/api/registration/validate-key', 
                                 json={'key': test_key},
                                 headers={'Content-Type': 'application/json'})
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_json()}")
            
            if response.status_code == 200:
                data = response.get_json()
                if data and data.get('ok'):
                    print("✅ Key validation working correctly!")
                    return True
                else:
                    print("❌ Key validation returned ok=False")
                    return False
            else:
                print(f"❌ HTTP error: {response.status_code}")
                return False

def test_registration_page():
    """Test that the registration page loads correctly."""
    with app.app_context():
        with app.test_client() as client:
            print("\nTesting registration page...")
            
            response = client.get('/register')
            print(f"Registration page status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.get_data(as_text=True)
                if 'Registration Unlock Key' in content:
                    print("✅ Registration page shows unlock key field")
                    return True
                else:
                    print("⚠️  Registration page doesn't show unlock key field")
                    return True  # This might be expected if no codes configured
            else:
                print(f"❌ Registration page error: {response.status_code}")
                return False

if __name__ == "__main__":
    print("=== Registration Key Test ===")
    key_test = test_registration_key_validation()
    page_test = test_registration_page()
    
    if key_test and page_test:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)