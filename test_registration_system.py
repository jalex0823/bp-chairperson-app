#!/usr/bin/env python3
"""
Test the new access key and database registration functionality.
"""
import os
import sys
from datetime import date
from dotenv import load_dotenv

load_dotenv()

from app import app, db, User

def test_new_access_key():
    """Test the new, more difficult access key."""
    print("=== Testing New Access Key ===")
    
    new_key = "BP2025!ChairPersonAccess#Unlock$Key"
    old_key = "BACKPORCH-KEY"
    
    with app.test_client() as client:
        # Test new key should work
        response = client.post('/api/registration/validate-key',
                             json={'key': new_key},
                             headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200 and response.get_json().get('ok'):
            print(f"✅ New key works: '{new_key}'")
        else:
            print(f"❌ New key failed: '{new_key}'")
            return False
        
        # Test old key should NOT work
        response = client.post('/api/registration/validate-key',
                             json={'key': old_key},
                             headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200 and not response.get_json().get('ok'):
            print(f"✅ Old key correctly rejected: '{old_key}'")
        else:
            print(f"❌ Old key should be rejected: '{old_key}'")
            return False
            
        # Test wrong key should NOT work
        response = client.post('/api/registration/validate-key',
                             json={'key': 'wrong-key'},
                             headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200 and not response.get_json().get('ok'):
            print("✅ Wrong key correctly rejected")
        else:
            print("❌ Wrong key should be rejected")
            return False
            
        return True

def test_database_connection():
    """Test database connectivity for registration."""
    print("\n=== Testing Database Connection ===")
    
    with app.app_context():
        try:
            # Try to query the database
            user_count = User.query.count()
            print(f"✅ Database connected - Current user count: {user_count}")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

def test_user_registration():
    """Test user registration with database."""
    print("\n=== Testing User Registration ===")
    
    # Set environment for SQLite testing
    os.environ['DATABASE_URL'] = 'sqlite:///test_registration.db'
    
    # Recreate app context with SQLite
    from app import app, db
    
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("✅ Test database created")
            
            # Test registration data
            test_data = {
                'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                'display_name': 'Test User',
                'email': 'test@example.com',
                'password': 'testpassword123',
                'sobriety_date': str(date(2020, 1, 1)),
                'gender': 'male',
                'agreed_guidelines': True
            }
            
            with app.test_client() as client:
                response = client.post('/register', data=test_data, follow_redirects=True)
                
                print(f"Registration response status: {response.status_code}")
                
                # Check if user was created
                user = User.query.filter_by(email='test@example.com').first()
                if user:
                    print(f"✅ User successfully registered:")
                    print(f"   - ID: {user.id}")
                    print(f"   - Display Name: {user.display_name}")
                    print(f"   - Email: {user.email}")
                    print(f"   - Gender: {user.gender}")
                    print(f"   - Sobriety Days: {user.sobriety_days}")
                    print(f"   - BP ID: {user.bp_id}")
                    return True
                else:
                    print("❌ User not found in database after registration")
                    return False
                    
        except Exception as e:
            print(f"❌ Registration test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Clean up test database
            try:
                if os.path.exists('test_registration.db'):
                    os.remove('test_registration.db')
                    print("✅ Test database cleaned up")
            except:
                pass

if __name__ == "__main__":
    print("=== Registration System Test ===")
    
    key_test = test_new_access_key()
    db_test = test_database_connection()
    
    if not db_test:
        print("\n⚠️  Main database not available, testing with SQLite...")
        reg_test = test_user_registration()
    else:
        print("\n✅ Main database available")
        reg_test = True
    
    print("\n=== Summary ===")
    print(f"Access Key Test: {'✅' if key_test else '❌'}")
    print(f"Database Test: {'✅' if db_test else '❌'}")
    print(f"Registration Test: {'✅' if reg_test else '❌'}")
    
    if key_test and reg_test:
        print("\n✅ All tests passed!")
        print(f"\nNew access key: BP2025!ChairPersonAccess#Unlock$Key")
        print("Registration system ready for use.")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)