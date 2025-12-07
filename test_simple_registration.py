#!/usr/bin/env python3
"""
Simple registration test using Flask app context to debug form validation.
"""
import os
import tempfile
from datetime import date
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for testing  
test_db_path = os.path.join(tempfile.gettempdir(), 'bp_simple_test.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

from app import app, db, User, RegisterForm

def test_form_validation_directly():
    """Test form validation directly without HTTP requests."""
    print("=== Direct Form Validation Test ===")
    
    with app.app_context():
        try:
            db.create_all()
            
            # Create form data exactly as it would come from the browser
            form_data = {
                'display_name': 'Test User',
                'email': 'test@example.com', 
                'password': 'TestPass123!',
                'sobriety_date': date(2022, 1, 15),
                'gender': 'male',
                'agreed_guidelines': True
            }
            
            # Test form validation
            form = RegisterForm(data=form_data)
            
            print(f"Form validation result: {form.validate()}")
            
            if form.errors:
                print("Form validation errors:")
                for field, errors in form.errors.items():
                    print(f"  - {field}: {errors}")
                return False
            else:
                print("✅ Form validation passed")
                
                # Test user creation manually
                user = User(
                    display_name=form_data['display_name'],
                    email=form_data['email'],
                    is_admin=False,
                    sobriety_days=1000,  # Approximate
                    agreed_guidelines=form_data['agreed_guidelines'],
                    gender=form_data['gender']
                )
                user.set_password(form_data['password'])
                
                db.session.add(user)
                db.session.commit()
                
                print(f"✅ User created manually: {user.bp_id}")
                
                # Verify user can be retrieved
                retrieved = User.query.filter_by(email='test@example.com').first()
                if retrieved:
                    print(f"✅ User retrieved: {retrieved.display_name}")
                    print(f"   Password check: {retrieved.check_password('TestPass123!')}")
                    return True
                else:
                    print("❌ Could not retrieve saved user")
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

def test_access_code_in_registration():
    """Test the access code validation in the registration flow."""
    print("\n=== Access Code Integration Test ===")
    
    test_db_path2 = os.path.join(tempfile.gettempdir(), 'bp_access_test.db') 
    os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path2}'
    
    # Reload app with new database
    from importlib import reload
    import app as app_module
    reload(app_module)
    
    with app_module.app.app_context():
        try:
            app_module.db.create_all()
            
            # Test invalid access code
            print("1. Testing invalid access code...")
            with app_module.app.test_client() as client:
                invalid_data = {
                    'access_code': 'WRONG-KEY',
                    'display_name': 'Test User',
                    'email': 'test@example.com',
                    'password': 'TestPass123!', 
                    'sobriety_date': '2022-01-15',
                    'gender': 'male',
                    'agreed_guidelines': True
                }
                
                response = client.post('/register', data=invalid_data)
                if response.status_code == 200 and 'Invalid access code' in response.get_data(as_text=True):
                    print("✅ Invalid access code correctly rejected")
                else:
                    print("❌ Invalid access code not handled properly")
                    return False
            
            # Test valid access code
            print("2. Testing valid access code...")
            with app_module.app.test_client() as client:
                # Get CSRF token first
                get_resp = client.get('/register')
                content = get_resp.get_data(as_text=True)
                csrf_start = content.find('name="csrf_token" value="') + len('name="csrf_token" value="')
                csrf_end = content.find('"', csrf_start)
                csrf_token = content[csrf_start:csrf_end] if csrf_start > 25 else ''
                
                valid_data = {
                    'csrf_token': csrf_token,
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'Valid User',
                    'email': 'valid@example.com',
                    'password': 'ValidPass123!',
                    'sobriety_date': '2022-01-15', 
                    'gender': 'female',
                    'agreed_guidelines': True
                }
                
                response = client.post('/register', data=valid_data, follow_redirects=False)
                
                if response.status_code == 302:
                    print("✅ Valid access code accepted (redirected)")
                    
                    # Check if user was saved
                    user = app_module.User.query.filter_by(email='valid@example.com').first()
                    if user:
                        print(f"✅ User saved: {user.bp_id}")
                        return True
                    else:
                        print("❌ User not saved despite successful form")
                        return False
                else:
                    print(f"❌ Valid access code failed: status {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Access code test failed: {e}")
            return False
        finally:
            try:
                if os.path.exists(test_db_path2):
                    os.remove(test_db_path2)
            except:
                pass

if __name__ == "__main__":
    print("=== Simple Registration System Test ===")
    
    form_test = test_form_validation_directly()
    access_test = test_access_code_in_registration()
    
    print(f"\n=== Results ===")
    print(f"Form Validation: {'✅' if form_test else '❌'}")
    print(f"Access Code Integration: {'✅' if access_test else '❌'}")
    
    if form_test and access_test:
        print("\n🎉 Registration system working correctly!")
        print("✅ More secure access key implemented")
        print("✅ Database persistence confirmed") 
        print("✅ Form validation working")
        print("✅ Access code validation integrated")
    else:
        print("\n❌ Issues found in registration system")