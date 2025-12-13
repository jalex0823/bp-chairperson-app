#!/usr/bin/env python3
"""
Test the actual Flask app with a working registration key endpoint.
"""
import os
import sys
from dotenv import load_dotenv

# Set environment variables to bypass database issues
os.environ['SECRET_KEY'] = 'test-key-123'
os.environ['REGISTRATION_ACCESS_CODE'] = 'BACKPORCH-KEY'
os.environ['DATABASE_URL'] = 'sqlite:///test.db'  # Use SQLite for testing

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def create_test_db():
    """Create a minimal test database."""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Test database created")
            return True
        except Exception as e:
            print(f"❌ Database creation failed: {e}")
            return False

def test_registration_endpoint():
    """Test the registration key validation with real Flask app."""
    with app.app_context():
        with app.test_client() as client:
            print("Testing /api/registration/validate-key endpoint...")
            
            # Test correct key
            response = client.post('/api/registration/validate-key',
                                 json={'key': 'BACKPORCH-KEY'},
                                 headers={'Content-Type': 'application/json'})
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_json()}")
            
            if response.status_code == 200:
                data = response.get_json()
                if data and data.get('ok'):
                    print("✅ Registration key endpoint working!")
                    return True
                else:
                    print("❌ Endpoint returned ok=False")
                    return False
            else:
                print(f"❌ HTTP error: {response.status_code}")
                return False

def test_registration_page():
    """Test the registration page renders correctly."""
    with app.app_context():
        with app.test_client() as client:
            print("\nTesting /register page...")
            
            response = client.get('/register')
            print(f"Registration page status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Registration page loads successfully")
                return True
            else:
                print(f"❌ Registration page error: {response.status_code}")
                return False

if __name__ == "__main__":
    print("=== Testing Flask App with SQLite ===")
    
    db_ok = create_test_db()
    if db_ok:
        api_ok = test_registration_endpoint()
        page_ok = test_registration_page()
        
        if api_ok and page_ok:
            print("\n✅ All tests passed! The registration key system is working.")
            print("\nSuggestions:")
            print("1. Check your browser's Network tab to see if API calls are being made")
            print("2. Check browser console for JavaScript errors")
            print("3. Try clearing localStorage and testing again")
        else:
            print("\n❌ Some tests failed")
    else:
        print("\n❌ Database setup failed")