#!/usr/bin/env python3
"""
Final clean test of registration system
"""
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

def final_registration_test():
    """Clean final test of registration system"""
    print("=== FINAL REGISTRATION SYSTEM TEST ===")
    
    test_db_path = os.path.join(tempfile.gettempdir(), 'bp_final_clean_test.db')
    os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    from app import app, db, User
    
    # Clean testing configuration
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['STATIC_SCHEDULE_ENABLED'] = False  # Disable static schedule
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database ready")
            
            with app.test_client() as client:
                print("\n🔑 Testing access key validation...")
                
                # Test access key API
                api_response = client.post('/api/registration/validate-key',
                                         json={'key': 'BP2025!ChairPersonAccess#Unlock$Key'},
                                         headers={'Content-Type': 'application/json'})
                
                if api_response.status_code == 200 and api_response.get_json().get('ok'):
                    print("   ✅ Access key API working")
                else:
                    print("   ❌ Access key API failed")
                    return False
                
                print("\n📝 Testing user registration...")
                
                # Test user registration
                user_data = {
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'Final Test User',
                    'email': 'final@test.com',
                    'password': 'FinalTestPass123!',
                    'sobriety_date': '2020-01-01',
                    'gender': 'male',
                    'agreed_guidelines': 'y'
                }
                
                print(f"   Registering: {user_data['display_name']}")
                print(f"   Email: {user_data['email']}")
                
                reg_response = client.post('/register', data=user_data, follow_redirects=False)
                
                print(f"   Response status: {reg_response.status_code}")
                
                if reg_response.status_code == 302:
                    print("   ✅ Registration successful")
                    
                    # Check database
                    user = User.query.filter_by(email='final@test.com').first()
                    if user:
                        print(f"   ✅ User saved: {user.bp_id} - {user.display_name}")
                        
                        # Test password
                        if user.check_password('FinalTestPass123!'):
                            print("   ✅ Password verification working")
                        else:
                            print("   ❌ Password verification failed")
                            return False
                            
                    else:
                        print("   ❌ User not found in database")
                        return False
                        
                elif reg_response.status_code == 200:
                    print("   ❌ Registration failed - form validation error")
                    content = reg_response.get_data(as_text=True)
                    
                    if 'Invalid access code' in content:
                        print("      - Access code issue")
                    elif 'alert-danger' in content:
                        print("      - Form validation issue")
                    elif 'is-invalid' in content:
                        print("      - Field validation issue")
                    else:
                        print("      - Unknown issue")
                    
                    return False
                else:
                    print(f"   ❌ Unexpected status: {reg_response.status_code}")
                    return False
                
                print("\n🔄 Testing duplicate email prevention...")
                
                # Test duplicate email
                duplicate_data = user_data.copy()
                duplicate_data['display_name'] = 'Duplicate Test User'
                duplicate_data['password'] = 'DuplicatePass123!'
                
                dup_response = client.post('/register', data=duplicate_data)
                
                if dup_response.status_code == 200 and 'already exists' in dup_response.get_data(as_text=True):
                    print("   ✅ Duplicate email prevented")
                else:
                    print("   ❌ Duplicate email not handled properly")
                    return False
                
                print("\n🚫 Testing wrong access key...")
                
                # Test wrong access key
                wrong_data = user_data.copy()
                wrong_data['access_code'] = 'WRONG-KEY'
                wrong_data['email'] = 'wrong@test.com'
                wrong_data['display_name'] = 'Wrong Key User'
                
                wrong_response = client.post('/register', data=wrong_data)
                
                if wrong_response.status_code == 200 and 'Invalid access code' in wrong_response.get_data(as_text=True):
                    print("   ✅ Wrong access key rejected")
                else:
                    print("   ❌ Wrong access key not handled properly")
                    return False
                
                print(f"\n🎉 ALL TESTS PASSED!")
                return True
                
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
    success = final_registration_test()
    
    print("\n" + "="*50)
    if success:
        print("🎯 REGISTRATION SYSTEM FULLY WORKING!")
        print("="*50)
        print("✅ Access key validation")
        print("✅ Form submission")
        print("✅ Database registration")
        print("✅ Password security")
        print("✅ Duplicate prevention")
        print("✅ Access key enforcement")
        print("\n🔐 Secure Key: BP2025!ChairPersonAccess#Unlock$Key")
        print("🚀 System ready for production!")
    else:
        print("❌ REGISTRATION SYSTEM HAS ISSUES")
        print("="*50)
    print("="*50)