#!/usr/bin/env python3
"""
Final comprehensive test with clean database
"""
import os
import tempfile
import uuid
from dotenv import load_dotenv

load_dotenv()

print("=== FINAL COMPREHENSIVE TEST ===")
print("Testing all registration components\n")

# Create a unique test database each time
test_db_path = os.path.join(tempfile.gettempdir(), f'bp_final_test_{uuid.uuid4().hex}.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

from app import app, db, User

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

print("1. Testing Access Key API...")
with app.test_client() as client:
    response = client.post('/api/registration/validate-key',
                         json={'key': 'BP2025!ChairPersonAccess#Unlock$Key'},
                         headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200 and response.get_json().get('ok'):
        print("   ✅ Access key API works")
        api_working = True
    else:
        print("   ❌ Access key API failed")
        api_working = False

print("\n2. Testing Database Operations...")
with app.app_context():
    try:
        # Create fresh database
        db.create_all()
        
        # Test user creation
        user = User(
            display_name="Test User",
            email="test@example.com",
            is_admin=False,
            agreed_guidelines=True
        )
        user.set_password("TestPass123!")
        
        db.session.add(user)
        db.session.commit()
        
        # Verify user saved
        saved_user = User.query.filter_by(email="test@example.com").first()
        if saved_user and saved_user.check_password("TestPass123!"):
            print("   ✅ Database save and password verification works")
            db_working = True
        else:
            print("   ❌ Database save or password verification failed")
            db_working = False
            
    except Exception as e:
        print(f"   ❌ Database operations failed: {e}")
        db_working = False

print("\n3. Testing Complete Registration Flow...")
with app.test_client() as client:
    # Test successful registration
    response = client.post('/register', data={
        'display_name': 'Flow Test User',
        'email': 'flowtest@example.com',
        'password': 'FlowPass123!',
        'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
        'agreed_guidelines': True,
        'gender': 'male'
    }, follow_redirects=False)
    
    if response.status_code == 302:  # Redirect on success
        print("   ✅ Registration form submission successful")
        
        # Verify user was created in database
        with app.app_context():
            new_user = User.query.filter_by(email='flowtest@example.com').first()
            if new_user and new_user.check_password('FlowPass123!'):
                print("   ✅ User saved to database correctly")
                registration_working = True
            else:
                print("   ❌ User not found or password incorrect")
                registration_working = False
    else:
        print(f"   ❌ Registration failed with status {response.status_code}")
        registration_working = False

print("\n4. Testing Duplicate Email Prevention...")
with app.test_client() as client:
    # Try to register same email again
    response2 = client.post('/register', data={
        'display_name': 'Duplicate User',
        'email': 'flowtest@example.com',  # Same email
        'password': 'DupPass123!',
        'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
        'agreed_guidelines': True,
        'gender': 'female'
    })
    
    if response2.status_code == 200:  # Should stay on page
        # Check for error message in response
        if b'already exists' in response2.data or b'already registered' in response2.data:
            print("   ✅ Duplicate email correctly prevented with error message")
            duplicate_prevention = True
        else:
            print("   ❌ Duplicate email not prevented or no error message shown")
            duplicate_prevention = False
    else:
        print(f"   ❌ Unexpected response to duplicate email: {response2.status_code}")
        duplicate_prevention = False

print("\n5. Testing Invalid Access Code...")
with app.test_client() as client:
    response3 = client.post('/register', data={
        'display_name': 'Wrong Code User',
        'email': 'wrongcode@example.com',
        'password': 'WrongPass123!',
        'access_code': 'WRONG_CODE',
        'agreed_guidelines': True,
        'gender': 'male'
    })
    
    if response3.status_code == 200:  # Should stay on page
        if b'Invalid access code' in response3.data:
            print("   ✅ Invalid access code correctly rejected")
            access_code_validation = True
        else:
            print("   ❌ Invalid access code not rejected or no error message")
            access_code_validation = False
    else:
        print(f"   ❌ Unexpected response to invalid access code: {response3.status_code}")
        access_code_validation = False

# Clean up
try:
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
except:
    pass

# Summary
print("\n" + "="*50)
print("🎯 COMPREHENSIVE TEST RESULTS")
print("="*50)
print(f"{'✅' if api_working else '❌'} Access Key API: {'WORKING' if api_working else 'FAILED'}")
print(f"{'✅' if db_working else '❌'} Database Operations: {'WORKING' if db_working else 'FAILED'}")
print(f"{'✅' if registration_working else '❌'} Registration Flow: {'WORKING' if registration_working else 'FAILED'}")
print(f"{'✅' if duplicate_prevention else '❌'} Duplicate Email Prevention: {'WORKING' if duplicate_prevention else 'FAILED'}")
print(f"{'✅' if access_code_validation else '❌'} Access Code Validation: {'WORKING' if access_code_validation else 'FAILED'}")

all_working = all([api_working, db_working, registration_working, duplicate_prevention, access_code_validation])

print(f"\n🔐 Access Key: BP2025!ChairPersonAccess#Unlock$Key")
print(f"🎯 Overall Status: {'✅ ALL SYSTEMS WORKING!' if all_working else '⚠️ Some issues found'}")
print("="*50)