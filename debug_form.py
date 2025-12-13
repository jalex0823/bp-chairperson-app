#!/usr/bin/env python3
"""
Debug registration form submission to identify validation issues.
"""
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for testing
test_db_path = os.path.join(tempfile.gettempdir(), 'bp_debug_test.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

from app import app, db

def test_registration_form_debug():
    """Debug registration form validation issues."""
    print("=== Registration Form Debug Test ===")
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ Test database created")
            
            with app.test_client() as client:
                # First get the registration page to get CSRF token
                print("\n1. Getting registration page...")
                get_response = client.get('/register')
                print(f"   GET /register status: {get_response.status_code}")
                
                if get_response.status_code != 200:
                    print("❌ Can't access registration page")
                    return False
                
                # Extract CSRF token from the page
                content = get_response.get_data(as_text=True)
                csrf_start = content.find('name="csrf_token" value="') + len('name="csrf_token" value="')
                csrf_end = content.find('"', csrf_start)
                csrf_token = content[csrf_start:csrf_end] if csrf_start > 25 else ''
                
                print(f"   CSRF token extracted: {csrf_token[:20]}...")
                
                # Test registration with proper form data including CSRF
                print("\n2. Testing registration submission...")
                registration_data = {
                    'csrf_token': csrf_token,
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'Jane D.',
                    'email': 'jane.d@test.com',
                    'password': 'TestPassword123!',
                    'sobriety_date': '2022-01-15',
                    'gender': 'female',
                    'agreed_guidelines': True,
                    'submit': 'Create Chairperson Account'
                }
                
                reg_response = client.post('/register', 
                                         data=registration_data,
                                         follow_redirects=False)
                
                print(f"   POST /register status: {reg_response.status_code}")
                
                if reg_response.status_code == 302:
                    print("✅ Registration successful (redirected)")
                    location = reg_response.headers.get('Location', '')
                    print(f"   Redirected to: {location}")
                    
                    # Check if user was created
                    from app import User
                    user = User.query.filter_by(email='jane.d@test.com').first()
                    if user:
                        print(f"✅ User created: {user.display_name} (ID: {user.id})")
                        return True
                    else:
                        print("❌ User not found in database")
                        return False
                        
                elif reg_response.status_code == 200:
                    print("⚠️  Registration returned to form (validation error)")
                    content = reg_response.get_data(as_text=True)
                    
                    # Look for error messages
                    if 'alert-danger' in content:
                        start = content.find('alert-danger')
                        error_section = content[start:start+500]
                        print("   Error messages found:")
                        # Extract error text
                        if 'Invalid access code' in error_section:
                            print("   - Invalid access code")
                        if 'already exists' in error_section:
                            print("   - Email already exists")
                        if 'required' in error_section:
                            print("   - Required field missing")
                    
                    # Check for field validation errors
                    if 'is-invalid' in content:
                        print("   Form validation errors found")
                    
                    return False
                else:
                    print(f"❌ Unexpected status code: {reg_response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            try:
                if os.path.exists(test_db_path):
                    os.remove(test_db_path)
            except:
                pass

if __name__ == "__main__":
    test_registration_form_debug()