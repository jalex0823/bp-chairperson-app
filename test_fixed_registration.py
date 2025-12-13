#!/usr/bin/env python3
"""
Test the fixed registration form validation
"""
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

test_db_path = os.path.join(tempfile.gettempdir(), 'bp_fixed_test.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

def test_fixed_registration():
    """Test registration after form validation fixes"""
    print("=== Testing Fixed Registration Form ===")
    
    from app import app, db, User
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database created")
            
            with app.test_client() as client:
                # Get the registration page
                get_response = client.get('/register')
                if get_response.status_code != 200:
                    print("❌ Cannot access registration page")
                    return False
                
                content = get_response.get_data(as_text=True)
                print("✅ Registration page loaded")
                
                # Extract CSRF token
                csrf_start = content.find('name="csrf_token" value="') + len('name="csrf_token" value="')
                csrf_end = content.find('"', csrf_start)
                csrf_token = content[csrf_start:csrf_end] if csrf_start > 25 else ''
                
                print(f"✅ CSRF token extracted")
                
                # Test registration with all required fields
                registration_data = {
                    'csrf_token': csrf_token,
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'Fixed Test User',
                    'email': 'fixed@test.com',
                    'password': 'FixedPassword123!',
                    'sobriety_date': '2021-01-01',
                    'gender': 'female',
                    'agreed_guidelines': 'y'
                }
                
                print("\n📝 Submitting registration with fixed form...")
                print(f"   Access Code: {registration_data['access_code'][:25]}...")
                print(f"   Email: {registration_data['email']}")
                print(f"   Display Name: {registration_data['display_name']}")
                print(f"   Gender: {registration_data['gender']}")
                
                response = client.post('/register', 
                                     data=registration_data,
                                     follow_redirects=False)
                
                print(f"\n📥 Response status: {response.status_code}")
                
                if response.status_code == 302:
                    # Success - check redirect location
                    location = response.headers.get('Location', '')
                    print(f"✅ Registration successful! Redirected to: {location}")
                    
                    # Verify user in database
                    user = User.query.filter_by(email='fixed@test.com').first()
                    if user:
                        print(f"\n💾 User successfully saved:")
                        print(f"   ID: {user.id}")
                        print(f"   BP ID: {user.bp_id}")
                        print(f"   Name: {user.display_name}")
                        print(f"   Email: {user.email}")
                        print(f"   Gender: {user.gender}")
                        print(f"   Sobriety Days: {user.sobriety_days}")
                        print(f"   Guidelines Agreed: {user.agreed_guidelines}")
                        
                        # Test password
                        if user.check_password('FixedPassword123!'):
                            print(f"   ✅ Password verification successful")
                            
                            print(f"\n🎉 COMPLETE SUCCESS!")
                            print(f"   ✅ Form validation fixed")
                            print(f"   ✅ Access key integration working")
                            print(f"   ✅ Database save working")
                            print(f"   ✅ All fields properly processed")
                            
                            return True
                        else:
                            print(f"   ❌ Password verification failed")
                            return False
                    else:
                        print(f"❌ User not found in database")
                        return False
                        
                elif response.status_code == 200:
                    print(f"❌ Form validation still failing")
                    content = response.get_data(as_text=True)
                    
                    # Check for specific errors
                    if 'Invalid access code' in content:
                        print(f"   - Access code validation failed")
                    if 'alert-danger' in content:
                        print(f"   - Flash messages present")
                    if 'is-invalid' in content:
                        print(f"   - Field validation errors present")
                    
                    # Print any validation errors for debugging
                    if 'This field is required' in content:
                        print(f"   - Required field validation errors")
                    
                    return False
                else:
                    print(f"❌ Unexpected status: {response.status_code}")
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

def test_form_structure():
    """Test that the form structure is correct"""
    print("\n=== Testing Form Structure ===")
    
    from app import app, RegisterForm
    
    with app.app_context():
        with app.test_request_context():
            form = RegisterForm()
            
            print("📋 Form fields:")
            for field_name, field in form._fields.items():
                print(f"   - {field_name}: {type(field).__name__}")
            
            # Check that access_code field exists
            if hasattr(form, 'access_code'):
                print("✅ access_code field is present in form")
                return True
            else:
                print("❌ access_code field missing from form")
                return False

if __name__ == "__main__":
    print("=== Fixed Registration Form Test ===")
    
    form_structure_ok = test_form_structure()
    if form_structure_ok:
        registration_ok = test_fixed_registration()
        
        if registration_ok:
            print(f"\n🎯 FIXES SUCCESSFUL!")
            print(f"✅ Form validation issues resolved")
            print(f"✅ Registration with database now works")
            print(f"✅ Access key integration fixed")
        else:
            print(f"\n❌ Still have registration issues")
    else:
        print(f"\n❌ Form structure issues remain")