#!/usr/bin/env python3
"""
Debug registration form submission to identify specific validation issues
"""
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

test_db_path = os.path.join(tempfile.gettempdir(), 'bp_debug_flow.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

from app import app, db

def debug_registration_submission():
    """Debug registration form submission to see exact validation errors"""
    print("=== Registration Form Submission Debug ===")
    
    with app.app_context():
        try:
            db.create_all()
            
            with app.test_client() as client:
                # Get registration page
                get_response = client.get('/register')
                content = get_response.get_data(as_text=True)
                
                # Extract CSRF token
                csrf_start = content.find('name="csrf_token" value="') + len('name="csrf_token" value="')
                csrf_end = content.find('"', csrf_start)
                csrf_token = content[csrf_start:csrf_end] if csrf_start > 25 else ''
                
                print(f"✅ CSRF token: {csrf_token[:15]}...")
                
                # Test registration data
                registration_data = {
                    'csrf_token': csrf_token,
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'Debug User',
                    'email': 'debug@test.com',
                    'password': 'DebugPass123!',
                    'sobriety_date': '2020-01-01',
                    'gender': 'male',
                    'agreed_guidelines': True,  # This should be True, not 'y'
                    'submit': 'Create Chairperson Account'
                }
                
                print("📝 Submitting registration with debug data...")
                print(f"   Access code: {registration_data['access_code'][:20]}...")
                print(f"   Email: {registration_data['email']}")
                print(f"   Guidelines agreed: {registration_data['agreed_guidelines']}")
                
                response = client.post('/register', data=registration_data)
                
                print(f"📥 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    # Parse response for error messages
                    response_content = response.get_data(as_text=True)
                    
                    print("\n🔍 Analyzing response for errors...")
                    
                    # Check for flash messages
                    if 'alert-danger' in response_content:
                        print("   ⚠️  Flash error messages found:")
                        # Try to extract error messages
                        start = response_content.find('alert-danger')
                        end = response_content.find('</div>', start)
                        if start != -1 and end != -1:
                            error_section = response_content[start:end]
                            if 'Invalid access code' in error_section:
                                print("      - Invalid access code")
                            if 'already exists' in error_section:
                                print("      - Email already exists")
                            if 'Database' in error_section:
                                print("      - Database error")
                    
                    # Check for field validation errors
                    if 'is-invalid' in response_content:
                        print("   ⚠️  Field validation errors found:")
                        # Look for specific field errors
                        fields = ['display_name', 'email', 'password', 'sobriety_date', 'gender', 'agreed_guidelines']
                        for field in fields:
                            if f'id="{field}"' in response_content and 'is-invalid' in response_content[response_content.find(f'id="{field}"'):response_content.find(f'id="{field}"')+200]:
                                print(f"      - {field} field has validation error")
                    
                    # Check if access codes are configured properly
                    if 'access_codes_configured' in response_content:
                        if 'true' in response_content[response_content.find('access_codes_configured'):response_content.find('access_codes_configured')+50]:
                            print("   ✅ Access codes are properly configured")
                        else:
                            print("   ❌ Access codes not configured")
                    
                    # Look for any obvious error indicators
                    if 'error' in response_content.lower():
                        print("   ⚠️  The word 'error' found in response")
                    
                    if len([line for line in response_content.split('\n') if 'Invalid' in line or 'required' in line]) > 0:
                        print("   ⚠️  Validation messages found in response")
                
                elif response.status_code == 302:
                    print("✅ Registration successful - form submitted correctly")
                    return True
                
                print(f"\n📄 Response content preview:")
                lines = response_content.split('\n')[:50]  # First 50 lines
                for i, line in enumerate(lines):
                    if 'alert' in line or 'error' in line.lower() or 'invalid' in line.lower():
                        print(f"   Line {i+1}: {line.strip()}")
                
                return False
                
        except Exception as e:
            print(f"❌ Debug failed: {e}")
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
    debug_registration_submission()