#!/usr/bin/env python3
"""
Focused test on duplicate email handling
"""
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

print("=== DUPLICATE EMAIL TEST ===")

test_db_path = os.path.join(tempfile.gettempdir(), 'bp_dup_test.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

from app import app, db, User

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

with app.app_context():
    try:
        # Create database
        db.create_all()
        
        print("1. Creating first user...")
        user1 = User(
            display_name="First User",
            email="duplicate@test.com",
            is_admin=False,
            agreed_guidelines=True
        )
        user1.set_password("Pass123!")
        
        db.session.add(user1)
        db.session.commit()
        
        # Check user exists
        check_user = User.query.filter_by(email="duplicate@test.com").first()
        if check_user:
            print("   ✅ First user created successfully")
            print(f"   User ID: {check_user.id}")
        else:
            print("   ❌ First user not found")
            
        print("\n2. Attempting to create duplicate user...")
        user2 = User(
            display_name="Duplicate User", 
            email="duplicate@test.com",  # Same email
            is_admin=False,
            agreed_guidelines=True
        )
        user2.set_password("Pass456!")
        
        try:
            db.session.add(user2)
            db.session.commit()
            print("   ❌ Duplicate user was allowed - this is wrong")
            
            # Check how many users with this email exist
            all_users = User.query.filter_by(email="duplicate@test.com").all()
            print(f"   Found {len(all_users)} users with email duplicate@test.com")
            
        except Exception as db_error:
            print(f"   ✅ Database correctly rejected duplicate: {db_error}")
            db.session.rollback()
            
        print("\n3. Testing form validation...")
        with app.test_client() as client:
            # First registration (should work)
            response1 = client.post('/register', data={
                'display_name': 'Form User 1',
                'email': 'formtest@test.com',
                'password': 'FormPass123!',
                'confirm_password': 'FormPass123!',
                'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                'agreed_guidelines': True
            })
            print(f"   First form submission: {response1.status_code}")
            
            # Second registration with same email (should fail)
            response2 = client.post('/register', data={
                'display_name': 'Form User 2', 
                'email': 'formtest@test.com',  # Same email
                'password': 'FormPass456!',
                'confirm_password': 'FormPass456!',
                'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                'agreed_guidelines': True
            })
            print(f"   Duplicate form submission: {response2.status_code}")
            
            if response2.status_code == 200:
                # Check if error message is in response
                if b'already registered' in response2.data or b'already exists' in response2.data:
                    print("   ✅ Form correctly shows duplicate email error")
                else:
                    print("   ❌ Form should show duplicate email error")
            else:
                print("   ❌ Form handled duplicate incorrectly")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
        except:
            pass

print("\nTest complete.")