#!/usr/bin/env python3
"""
Test the Flask app registration functionality with real app context.
"""
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import the actual app
from app import app

def test_registration_key_endpoint():
    """Test the registration API endpoint."""
    print("=== Testing Registration Key API ===")
    
    with app.test_client() as client:
        # Test the API endpoint directly
        print("Testing /api/registration/validate-key...")
        
        response = client.post('/api/registration/validate-key',
                             json={'key': 'BACKPORCH-KEY'},
                             headers={'Content-Type': 'application/json'})
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"Response: {data}")
            if data and data.get('ok'):
                print("✅ API endpoint working correctly!")
                return True
            else:
                print("❌ API returned ok=False")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")
            return False

def test_registration_page():
    """Test that the registration page loads."""
    print("\n=== Testing Registration Page ===")
    
    with app.test_client() as client:
        print("Testing /register page...")
        
        response = client.get('/register')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            if 'Registration Unlock Key' in content:
                print("✅ Registration page shows unlock key field")
                if 'api/registration/validate-key' in content:
                    print("✅ JavaScript API call present")
                else:
                    print("❌ JavaScript API call missing")
                return True
            else:
                print("❌ Registration page doesn't show unlock key field")
                return False
        else:
            print(f"❌ Registration page failed: {response.status_code}")
            error_text = response.get_data(as_text=True)
            print(f"Error: {error_text[:500]}...")
            return False

if __name__ == "__main__":
    try:
        api_test = test_registration_key_endpoint()
        page_test = test_registration_page()
        
        if api_test and page_test:
            print("\n✅ Registration key system is working!")
            print("\nIf it's still not working in your browser:")
            print("1. Clear browser cache and localStorage")
            print("2. Check browser Network tab for failed API calls")
            print("3. Check browser Console tab for JavaScript errors")
        else:
            print("\n❌ Some tests failed!")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()