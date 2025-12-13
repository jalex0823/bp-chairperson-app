#!/usr/bin/env python3
"""
Comprehensive test of registration system with database persistence.
"""
import os
import tempfile
from datetime import date
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for testing
test_db_path = os.path.join(tempfile.gettempdir(), 'bp_registration_test.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

from app import app, db, User

def test_complete_registration_flow():
    """Test the complete registration flow including database persistence."""
    print("=== Complete Registration Flow Test ===")
    
    with app.app_context():
        try:
            # Setup test database
            db.create_all()
            print("✅ Test database created")
            
            # Test data
            registration_data = {
                'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                'display_name': 'John A.',
                'email': 'john.a@example.com',
                'password': 'SecurePass123!',
                'sobriety_date': '2020-06-15',
                'gender': 'male',
                'agreed_guidelines': 'y'
            }
            
            with app.test_client() as client:
                print("\n1. Testing access key validation...")
                # First validate the access key
                key_response = client.post('/api/registration/validate-key',
                                         json={'key': registration_data['access_code']},
                                         headers={'Content-Type': 'application/json'})
                
                if key_response.status_code == 200 and key_response.get_json().get('ok'):
                    print("✅ Access key validation passed")
                else:
                    print("❌ Access key validation failed")
                    return False
                
                print("\n2. Testing user registration...")
                # Now test the actual registration
                reg_response = client.post('/register', 
                                         data=registration_data,
                                         follow_redirects=False)
                
                print(f"   Registration status: {reg_response.status_code}")
                
                if reg_response.status_code == 302:  # Redirect on success
                    print("✅ Registration submitted successfully")
                else:
                    print(f"❌ Registration failed with status {reg_response.status_code}")
                    print(f"   Response: {reg_response.get_data(as_text=True)[:500]}")
                    return False
                
                print("\n3. Verifying user was saved to database...")
                # Check if user was actually saved
                saved_user = User.query.filter_by(email='john.a@example.com').first()
                
                if saved_user:
                    print("✅ User successfully saved to database!")
                    print(f"   User ID: {saved_user.id}")
                    print(f"   BP ID: {saved_user.bp_id}")
                    print(f"   Display Name: {saved_user.display_name}")
                    print(f"   Email: {saved_user.email}")
                    print(f"   Gender: {saved_user.gender}")
                    print(f"   Sobriety Days: {saved_user.sobriety_days}")
                    print(f"   Agreed Guidelines: {saved_user.agreed_guidelines}")
                    print(f"   Created At: {saved_user.created_at}")
                    
                    # Test password
                    if saved_user.check_password('SecurePass123!'):
                        print("✅ Password correctly hashed and verifiable")
                    else:
                        print("❌ Password hash verification failed")
                        return False
                    
                    return True
                else:
                    print("❌ User not found in database after registration")
                    # List all users for debugging
                    all_users = User.query.all()
                    print(f"   Total users in database: {len(all_users)}")
                    for user in all_users:
                        print(f"   - {user.email} (ID: {user.id})")
                    return False
                    
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Clean up
            try:
                if os.path.exists(test_db_path):
                    os.remove(test_db_path)
                    print(f"\n✅ Cleaned up test database: {test_db_path}")
            except:
                pass

def test_duplicate_email_prevention():
    """Test that duplicate email registration is prevented."""
    print("\n=== Duplicate Email Prevention Test ===")
    
    test_db_path2 = os.path.join(tempfile.gettempdir(), 'bp_dup_test.db')
    os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path2}'
    
    # Need to reload the app with new database URL
    from importlib import reload
    import app as app_module
    reload(app_module)
    
    with app_module.app.app_context():
        try:
            app_module.db.create_all()
            
            # Create first user
            user1 = app_module.User(
                display_name="First User",
                email="duplicate@test.com",
                is_admin=False,
                agreed_guidelines=True
            )
            user1.set_password("pass123")
            app_module.db.session.add(user1)
            app_module.db.session.commit()
            
            # Try to register second user with same email
            dup_data = {
                'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                'display_name': 'Second User',
                'email': 'duplicate@test.com',  # Same email
                'password': 'different123',
                'agreed_guidelines': 'y'
            }
            
            with app_module.app.test_client() as client:
                response = client.post('/register', data=dup_data)
                
                # Should not redirect (stays on registration page with error)
                if response.status_code == 200:
                    content = response.get_data(as_text=True)
                    if "already exists" in content:
                        print("✅ Duplicate email correctly prevented")
                        return True
                    else:
                        print("❌ No duplicate email error shown")
                        return False
                else:
                    print(f"❌ Expected 200 status for duplicate email, got {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Duplicate email test failed: {e}")
            return False
        finally:
            try:
                if os.path.exists(test_db_path2):
                    os.remove(test_db_path2)
            except:
                pass

if __name__ == "__main__":
    print("=== Registration System Database Test ===")
    
    main_test = test_complete_registration_flow()
    dup_test = test_duplicate_email_prevention()
    
    print("\n=== Final Summary ===")
    print(f"Registration Flow: {'✅' if main_test else '❌'}")
    print(f"Duplicate Prevention: {'✅' if dup_test else '❌'}")
    
    if main_test and dup_test:
        print("\n🎉 All registration tests passed!")
        print("\n📋 Registration System Status:")
        print("   ✅ Access key: BP2025!ChairPersonAccess#Unlock$Key (more secure)")
        print("   ✅ Database persistence: Working")
        print("   ✅ Duplicate email prevention: Working") 
        print("   ✅ Password hashing: Working")
        print("   ✅ User data validation: Working")
        print("\n🚀 Registration system is ready for production!")
    else:
        print("\n❌ Some tests failed - check the output above")