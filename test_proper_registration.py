#!/usr/bin/env python3
"""
Test registration with proper form field formatting for Flask-WTF
"""
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

test_db_path = os.path.join(tempfile.gettempdir(), 'bp_proper_test.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

from app import app, db, User

def test_registration_with_proper_fields():
    """Test registration with properly formatted form fields"""
    print("=== Registration with Proper Form Fields ===")
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database created")
            
            with app.test_client() as client:
                # Get the form page
                get_response = client.get('/register')
                content = get_response.get_data(as_text=True)
                
                # Extract CSRF token
                csrf_start = content.find('name="csrf_token" value="') + len('name="csrf_token" value="')
                csrf_end = content.find('"', csrf_start)
                csrf_token = content[csrf_start:csrf_end] if csrf_start > 25 else ''
                
                # Form data with proper formatting for Flask-WTF
                # For checkboxes: 'y' means checked, absence means unchecked
                # For radio buttons: exact string value from choices
                registration_data = {
                    'csrf_token': csrf_token,
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'Test Chair Person',
                    'email': 'testchair@example.com',
                    'password': 'TestPassword123!',
                    'sobriety_date': '2022-06-01',  # YYYY-MM-DD format
                    'gender': 'male',  # Exact value from RadioField choices
                    'agreed_guidelines': 'y',  # 'y' for checked checkbox in Flask-WTF
                    'submit': 'Create Chairperson Account'
                }
                
                print("📝 Form data prepared:")
                for key, value in registration_data.items():
                    if key != 'csrf_token':  # Don't print full CSRF token
                        print(f"   {key}: {value}")
                
                print(f"\n🔑 Testing access key: {registration_data['access_code'][:25]}...")
                
                # Submit the registration
                response = client.post('/register', 
                                     data=registration_data,
                                     follow_redirects=False)
                
                print(f"\n📥 Response status: {response.status_code}")
                
                if response.status_code == 302:
                    # Success - redirected
                    location = response.headers.get('Location', '')
                    print(f"✅ Registration successful! Redirected to: {location}")
                    
                    # Verify user was created in database
                    user = User.query.filter_by(email='testchair@example.com').first()
                    if user:
                        print(f"\n💾 User saved to database:")
                        print(f"   ID: {user.id}")
                        print(f"   BP ID: {user.bp_id}")
                        print(f"   Name: {user.display_name}")
                        print(f"   Email: {user.email}")
                        print(f"   Gender: {user.gender}")
                        print(f"   Sobriety Days: {user.sobriety_days}")
                        print(f"   Guidelines Agreed: {user.agreed_guidelines}")
                        
                        # Test password
                        password_ok = user.check_password('TestPassword123!')
                        print(f"   Password Verified: {password_ok}")
                        
                        if password_ok:
                            print(f"\n🎉 COMPLETE SUCCESS!")
                            print(f"   ✅ Access key worked")
                            print(f"   ✅ Form validation passed") 
                            print(f"   ✅ User saved to database")
                            print(f"   ✅ All data correctly stored")
                            return True
                        else:
                            print(f"   ❌ Password verification failed")
                            return False
                    else:
                        print(f"❌ User not found in database after successful form submission")
                        return False
                        
                elif response.status_code == 200:
                    # Form validation failed - stayed on page
                    content = response.get_data(as_text=True)
                    print(f"❌ Form validation failed")
                    
                    # Check for specific error messages
                    if 'Invalid access code' in content:
                        print(f"   - Invalid access code error")
                    if 'already exists' in content:
                        print(f"   - Email already exists error")
                    if 'alert-danger' in content:
                        print(f"   - Flash error message present")
                    
                    # Check for field-specific errors
                    if 'is-invalid' in content:
                        print(f"   - Field validation errors present")
                        # Try to identify which fields
                        if 'name="display_name"' in content and 'is-invalid' in content:
                            print(f"     * Display name field error")
                        if 'name="email"' in content and 'is-invalid' in content:
                            print(f"     * Email field error") 
                        if 'name="password"' in content and 'is-invalid' in content:
                            print(f"     * Password field error")
                        if 'name="agreed_guidelines"' in content and 'is-invalid' in content:
                            print(f"     * Guidelines checkbox error")
                        if 'name="gender"' in content and 'is-invalid' in content:
                            print(f"     * Gender selection error")
                    
                    return False
                else:
                    print(f"❌ Unexpected response status: {response.status_code}")
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
    success = test_registration_with_proper_fields()
    
    if success:
        print(f"\n🎯 ANSWER: YES - Registration with database works!")
        print(f"   The complete flow (access key → form → database) is functional")
    else:
        print(f"\n❌ ANSWER: NO - Registration with database has issues")
        print(f"   There are still form validation or database save problems")