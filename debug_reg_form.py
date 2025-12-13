#!/usr/bin/env python3
"""
Debug why registration form is failing
"""
import os
import tempfile
import uuid
from dotenv import load_dotenv

load_dotenv()

print("=== DEBUGGING REGISTRATION FORM ===")

# Create a unique test database
test_db_path = os.path.join(tempfile.gettempdir(), f'bp_debug_{uuid.uuid4().hex}.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

from app import app, db, User

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

with app.app_context():
    db.create_all()

with app.test_client() as client:
    # First, get the registration page to see what fields are expected
    print("1. Getting registration form...")
    get_response = client.get('/register')
    print(f"   GET /register status: {get_response.status_code}")
    
    print("\n2. Attempting registration...")
    response = client.post('/register', data={
        'display_name': 'Debug Test User',
        'email': 'debug@example.com',
        'password': 'DebugPass123!',
        'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
        'agreed_guidelines': True,
        'gender': 'male'  # Required field!
    }, follow_redirects=False)
    
    print(f"   POST /register status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    
    # Check if there's a redirect
    if 'Location' in response.headers:
        print(f"   Redirect to: {response.headers['Location']}")
    
    # Show response content (first 1000 chars)
    response_text = response.data.decode('utf-8', errors='ignore')
    if len(response_text) > 1000:
        print(f"   Response content (first 1000 chars):\n{response_text[:1000]}...")
    else:
        print(f"   Response content:\n{response_text}")
    
    # Check if user was created despite the status
    with app.app_context():
        user = User.query.filter_by(email='debug@example.com').first()
        if user:
            print(f"   ✅ User found in database: {user.display_name} (ID: {user.id})")
        else:
            print("   ❌ User not found in database")

# Clean up
try:
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
except:
    pass