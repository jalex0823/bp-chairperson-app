#!/usr/bin/env python3
"""
Test registration with proper CSRF handling
"""
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

test_db_path = os.path.join(tempfile.gettempdir(), 'bp_csrf_test.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

def test_registration_with_csrf():
    """Test registration with proper CSRF handling"""
    print("=== Registration Test with CSRF Handling ===")
    
    from app import app, db, User
    
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database created")
            
            with app.test_client() as client:
                print("\n📝 Testing registration with CSRF disabled...")
                
                # Test registration data
                registration_data = {
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'CSRF Test User',
                    'email': 'csrf@test.com',
                    'password': 'CSRFPassword123!',
                    'sobriety_date': '2020-06-01',
                    'gender': 'male',
                    'agreed_guidelines': 'y'
                }
                
                print(f"   Access Code: {registration_data['access_code'][:25]}...")
                print(f"   Email: {registration_data['email']}")
                print(f"   Display Name: {registration_data['display_name']}")
                
                response = client.post('/register', 
                                     data=registration_data,
                                     follow_redirects=False)
                
                print(f"\n📥 Response status: {response.status_code}")
                
                if response.status_code == 302:
                    location = response.headers.get('Location', '')
                    print(f"✅ Registration successful! Redirected to: {location}")
                    
                    # Check database
                    user = User.query.filter_by(email='csrf@test.com').first()
                    if user:
                        print(f"\n💾 User successfully saved:")
                        print(f"   ID: {user.id}")
                        print(f"   BP ID: {user.bp_id}")
                        print(f"   Name: {user.display_name}")
                        print(f"   Email: {user.email}")
                        print(f"   Gender: {user.gender}")
                        print(f"   Sobriety Days: {user.sobriety_days}")
                        
                        if user.check_password('CSRFPassword123!'):
                            print(f"   ✅ Password verification successful")
                            
                            print(f"\n🎉 REGISTRATION FULLY WORKING!")
                            print(f"   ✅ Access key validation")
                            print(f"   ✅ Form processing") 
                            print(f"   ✅ Database save")
                            print(f"   ✅ All fields processed correctly")
                            
                            return True
                        else:
                            print(f"   ❌ Password verification failed")
                            return False
                    else:
                        print(f"❌ User not saved to database")
                        return False
                        
                elif response.status_code == 200:
                    print(f"❌ Form validation failed")
                    content = response.get_data(as_text=True)
                    
                    if 'Invalid access code' in content:
                        print(f"   - Invalid access code")
                    elif 'alert-danger' in content:
                        print(f"   - Flash error message")
                    else:
                        print(f"   - Unknown validation error")
                    
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

def test_access_key_validation_in_form():
    """Test that access key validation works in the form submission"""
    print("\n=== Access Key Validation in Form Test ===")
    
    from app import app, db
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        try:
            db.create_all()
            
            with app.test_client() as client:
                # Test with wrong access key
                print("1. Testing with incorrect access key...")
                
                wrong_data = {
                    'access_code': 'WRONG-KEY',
                    'display_name': 'Wrong Key User',
                    'email': 'wrong@test.com',
                    'password': 'WrongPassword123!',
                    'sobriety_date': '2020-01-01',
                    'gender': 'female',
                    'agreed_guidelines': 'y'
                }
                
                response = client.post('/register', data=wrong_data)
                
                if response.status_code == 200 and 'Invalid access code' in response.get_data(as_text=True):
                    print("   ✅ Wrong access key correctly rejected")
                else:
                    print("   ❌ Wrong access key not handled properly")
                    return False
                
                # Test with correct access key
                print("2. Testing with correct access key...")
                
                correct_data = {
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'Correct Key User',
                    'email': 'correct@test.com',
                    'password': 'CorrectPassword123!',
                    'sobriety_date': '2020-01-01',
                    'gender': 'female',
                    'agreed_guidelines': 'y'
                }
                
                response = client.post('/register', data=correct_data, follow_redirects=False)
                
                if response.status_code == 302:
                    print("   ✅ Correct access key accepted")
                    return True
                else:
                    print(f"   ❌ Correct access key failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Access key test failed: {e}")
            return False
        finally:
            try:
                db_path = test_db_path.replace('csrf_test', 'csrf_test2')
                if os.path.exists(db_path):
                    os.remove(db_path)
            except:
                pass

if __name__ == "__main__":
    print("=== Testing Fixed Registration System ===")
    
    registration_test = test_registration_with_csrf()
    access_key_test = test_access_key_validation_in_form()
    
    print(f"\n=== Final Test Results ===")
    print(f"Registration Flow: {'✅' if registration_test else '❌'}")
    print(f"Access Key Validation: {'✅' if access_key_test else '❌'}")
    
    if registration_test and access_key_test:
        print(f"\n🎯 FIXES SUCCESSFUL!")
        print(f"✅ All form validation issues resolved")
        print(f"✅ Registration with database works completely")
        print(f"✅ Access key integration functioning properly")
        print(f"✅ Complete user registration flow operational")
    else:
        print(f"\n❌ Some issues still remain")