#!/usr/bin/env python3
"""
Simple test of registration key validation without database connection.
"""
import os
import sys
import json
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_key_validation_logic():
    """Test the key validation logic directly."""
    print("=== Testing Registration Key Logic ===")
    
    # Test the configuration values
    from config import Config
    config = Config()
    
    access_code = getattr(config, 'REGISTRATION_ACCESS_CODE', None)
    access_codes = getattr(config, 'REGISTRATION_ACCESS_CODES', None)
    
    print(f"REGISTRATION_ACCESS_CODE: {access_code}")
    print(f"REGISTRATION_ACCESS_CODES: {access_codes}")
    
    # Simulate the validation logic from the app
    provided = "BACKPORCH-KEY"  # Test with default key
    
    valid_codes = set()
    if access_code:
        valid_codes.add(str(access_code).strip())
    if access_codes:
        for c in str(access_codes).split(','):
            c = c.strip()
            if c:
                valid_codes.add(c)
    
    print(f"Valid codes: {valid_codes}")
    print(f"Testing key: '{provided}'")
    
    ok = True
    if valid_codes:
        ok = provided in valid_codes
    
    print(f"Validation result: {ok}")
    
    if ok:
        print("✅ Key validation logic working correctly!")
    else:
        print("❌ Key validation failed!")
    
    return ok

def test_javascript_key():
    """Test what happens with an empty or incorrect key."""
    print("\n=== Testing with different keys ===")
    
    from config import Config
    config = Config()
    access_code = getattr(config, 'REGISTRATION_ACCESS_CODE', None)
    
    test_cases = [
        ("", "Empty key"),
        ("wrong-key", "Incorrect key"), 
        ("BACKPORCH-KEY", "Correct key"),
        ("backporch-key", "Lowercase version"),
        (" BACKPORCH-KEY ", "Key with spaces")
    ]
    
    for test_key, description in test_cases:
        valid_codes = set()
        if access_code:
            valid_codes.add(str(access_code).strip())
        
        provided = test_key.strip()
        ok = provided in valid_codes if valid_codes else True
        
        status = "✅" if ok else "❌"
        print(f"{status} {description}: '{test_key}' -> {ok}")

if __name__ == "__main__":
    test_key_validation_logic()
    test_javascript_key()