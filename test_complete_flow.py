#!/usr/bin/env python3
"""
Test the complete registration flow: access key unlock → form submission → database save
"""
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for reliable testing
test_db_path = os.path.join(tempfile.gettempdir(), 'bp_complete_flow_test.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

from app import app, db, User

def test_complete_registration_flow():
    """Test the complete flow: unlock form → submit registration → verify database save"""
    print("=== Complete Registration Flow Test ===")
    
    with app.app_context():
        try:
            # Setup test database
            db.create_all()
            print("✅ Test database created")
            
            with app.test_client() as client:
                print("\n🔑 STEP 1: Testing access key validation (form unlock)")
                
                # Test access key validation API
                key_response = client.post('/api/registration/validate-key',
                                         json={'key': 'BP2025!ChairPersonAccess#Unlock$Key'},
                                         headers={'Content-Type': 'application/json'})
                
                if key_response.status_code == 200 and key_response.get_json().get('ok'):
                    print("   ✅ Access key validates - form can be unlocked")
                else:
                    print("   ❌ Access key validation failed")
                    return False
                
                print("\n📝 STEP 2: Testing form submission with access key")
                
                # Get the registration page to extract CSRF token
                get_response = client.get('/register')
                if get_response.status_code != 200:
                    print("   ❌ Cannot access registration page")
                    return False
                
                # Extract CSRF token
                content = get_response.get_data(as_text=True)
                csrf_start = content.find('name="csrf_token" value="') + len('name="csrf_token" value="')
                csrf_end = content.find('"', csrf_start)
                csrf_token = content[csrf_start:csrf_end] if csrf_start > 25 else ''
                
                print(f"   ✅ CSRF token extracted: {csrf_token[:10]}...")
                
                # Submit complete registration form (including access code)
                registration_data = {
                    'csrf_token': csrf_token,
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',  # Access key in form submission
                    'display_name': 'Maria S.',
                    'email': 'maria.s@example.com',
                    'password': 'SecurePassword123!',
                    'sobriety_date': '2021-03-10',
                    'gender': 'female',
                    'agreed_guidelines': True
                }
                
                print("   📤 Submitting registration form with access key...")
                
                response = client.post('/register', 
                                     data=registration_data,
                                     follow_redirects=False)
                
                print(f"   📥 Response status: {response.status_code}")
                
                if response.status_code == 302:  # Redirect = success
                    location = response.headers.get('Location', '')
                    print(f"   ✅ Registration successful - redirected to: {location}")
                elif response.status_code == 200:
                    # Check for error messages
                    content = response.get_data(as_text=True)
                    if 'Invalid access code' in content:
                        print("   ❌ Access code validation failed in form submission")
                        return False
                    elif 'alert-danger' in content:
                        print("   ❌ Form validation errors occurred")
                        # Try to extract error message
                        if 'already exists' in content:
                            print("       - Email already exists")
                        return False
                    else:
                        print("   ❌ Registration failed for unknown reason")
                        return False
                else:
                    print(f"   ❌ Unexpected response status: {response.status_code}")
                    return False
                
                print("\n💾 STEP 3: Verifying database save")
                
                # Check if user was actually saved to database
                saved_user = User.query.filter_by(email='maria.s@example.com').first()
                
                if saved_user:
                    print("   ✅ User successfully saved to database!")
                    print(f"      - User ID: {saved_user.id}")
                    print(f"      - BP ID: {saved_user.bp_id}")
                    print(f"      - Display Name: {saved_user.display_name}")
                    print(f"      - Email: {saved_user.email}")
                    print(f"      - Gender: {saved_user.gender}")
                    print(f"      - Sobriety Days: {saved_user.sobriety_days}")
                    print(f"      - Guidelines Agreed: {saved_user.agreed_guidelines}")
                    
                    # Test password verification
                    if saved_user.check_password('SecurePassword123!'):
                        print("      - ✅ Password correctly hashed and verifiable")
                    else:
                        print("      - ❌ Password hash issue")
                        return False
                    
                    print(f"\n🎉 COMPLETE FLOW SUCCESS!")
                    print(f"   🔑 Access key unlocked form")
                    print(f"   📝 Form submitted with valid data")
                    print(f"   💾 User saved to database")
                    print(f"   🔒 Password properly hashed")
                    
                    return True
                else:
                    print("   ❌ User NOT found in database after registration")
                    
                    # Debug: check what users exist
                    all_users = User.query.all()
                    print(f"   📊 Total users in database: {len(all_users)}")
                    for user in all_users:
                        print(f"      - {user.email} (ID: {user.id})")
                    
                    return False
                    
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Cleanup
            try:
                if os.path.exists(test_db_path):
                    os.remove(test_db_path)
                    print(f"\n🧹 Cleaned up test database")
            except:
                pass

if __name__ == "__main__":
    print("=== Testing Complete Registration Flow ===")
    print("This tests: Access Key → Form Unlock → Form Submit → Database Save")
    print()
    
    success = test_complete_registration_flow()
    
    if success:
        print("\n🎯 FINAL RESULT: Complete registration flow is working!")
        print("   ✅ Access key unlocks form fields")
        print("   ✅ Form submission validates access key")  
        print("   ✅ User registration saves to database")
        print("   ✅ Password is properly hashed")
    else:
        print("\n❌ FINAL RESULT: Issues found in registration flow")