#!/usr/bin/env python3
"""
Quick test of registration key functionality.
"""
from app import app

print("=== Quick Registration Key Test ===")

# Test API endpoint
with app.test_client() as client:
    response = client.post('/api/registration/validate-key',
                         json={'key': 'BP2025!ChairPersonAccess#Unlock$Key'},
                         headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200 and response.get_json().get('ok'):
        print("✅ Registration key validation is WORKING!")
        print("   API endpoint: /api/registration/validate-key")
        print("   Valid key: BP2025!ChairPersonAccess#Unlock$Key")
        print()
        print("To test in browser:")
        print("1. Start the Flask app: python app.py")
        print("2. Go to: http://localhost:5000/register")
        print("3. Enter key: BP2025!ChairPersonAccess#Unlock$Key")
        print("4. Click Submit - form fields should unlock")
    else:
        print("❌ Registration key validation failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")