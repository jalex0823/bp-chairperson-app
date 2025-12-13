#!/usr/bin/env python3
"""
Debug script to help troubleshoot registration key issues.
"""
import os
from dotenv import load_dotenv

load_dotenv()

def check_configuration():
    """Check the current configuration."""
    print("=== Configuration Check ===")
    
    access_code = os.environ.get('REGISTRATION_ACCESS_CODE')
    access_codes = os.environ.get('REGISTRATION_ACCESS_CODES')
    registration_enabled = os.environ.get('REGISTRATION_ENABLED', 'true').lower()
    
    print(f"REGISTRATION_ENABLED: {registration_enabled}")
    print(f"REGISTRATION_ACCESS_CODE: {access_code}")
    print(f"REGISTRATION_ACCESS_CODES: {access_codes}")
    
    if not access_code and not access_codes:
        print("❌ No access codes configured!")
        print("   The registration form will not show unlock key fields.")
    elif access_code:
        print(f"✅ Using access code: {access_code}")
    elif access_codes:
        codes = [c.strip() for c in access_codes.split(',') if c.strip()]
        print(f"✅ Using access codes: {codes}")
    
    return access_code or access_codes

def test_manual_validation():
    """Manually test key validation logic."""
    print("\n=== Manual Key Validation Test ===")
    
    from config import Config
    config = Config()
    
    access_code = getattr(config, 'REGISTRATION_ACCESS_CODE', None)
    access_codes_raw = getattr(config, 'REGISTRATION_ACCESS_CODES', None)
    
    # Test keys
    test_keys = [
        'BP2025!ChairPersonAccess#Unlock$Key',
        'BACKPORCH-KEY',
        'bp2025!chairpersonaccess#unlock$key',
        'wrong-key',
        '',
        ' BP2025!ChairPersonAccess#Unlock$Key '
    ]
    
    for test_key in test_keys:
        # Simulate validation logic
        provided = test_key.strip()
        
        valid_codes = set()
        if access_code:
            valid_codes.add(str(access_code).strip())
        if access_codes_raw:
            for c in str(access_codes_raw).split(','):
                c = c.strip()
                if c:
                    valid_codes.add(c)
        
        ok = provided in valid_codes if valid_codes else True
        status = "✅" if ok else "❌"
        print(f"{status} '{test_key}' -> {ok}")

def show_browser_debug_tips():
    """Show tips for debugging in browser."""
    print("\n=== Browser Debug Tips ===")
    print("1. Open browser Developer Tools (F12)")
    print("2. Go to the Network tab")
    print("3. Visit the registration page")
    print("4. Enter the unlock key and click Submit")
    print("5. Check for:")
    print("   - POST request to /api/registration/validate-key")
    print("   - Response should be: {\"ok\": true}")
    print("   - No JavaScript errors in Console tab")
    print()
    print("6. Check Local Storage:")
    print("   - Open Application/Storage tab")
    print("   - Check localStorage for 'bp_access_code' entry")
    print()
    print("7. Common issues:")
    print("   - CORS errors (should not happen on same domain)")
    print("   - Network timeout (check server is running)")
    print("   - Wrong key (case sensitive)")

if __name__ == "__main__":
    has_codes = check_configuration()
    if has_codes:
        test_manual_validation()
    show_browser_debug_tips()