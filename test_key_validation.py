#!/usr/bin/env python3
"""Test registration key validation logic"""

# Simulate what the API endpoint does
def validate_key(provided, required_code, codes_list_raw):
    """Test key validation"""
    valid_codes = set()
    if required_code:
        valid_codes.add(str(required_code).strip())
    if codes_list_raw:
        for c in str(codes_list_raw).split(','):
            c = c.strip()
            if c:
                valid_codes.add(c)
    
    ok = True
    if valid_codes:
        ok = provided in valid_codes
    
    return ok, valid_codes

# Test with the key you entered
provided_key = "BP2025!ChairPersonAccess#Unlock$Key"

# Test with default config value
required_code = "BACKPORCH-KEY"
codes_list_raw = None

result, valid_codes = validate_key(provided_key, required_code, codes_list_raw)

print(f"Provided key: {provided_key}")
print(f"Required code: {required_code}")
print(f"Codes list: {codes_list_raw}")
print(f"Valid codes set: {valid_codes}")
print(f"Validation result: {result}")
print()

# Now test with the key you entered as the required code
required_code = "BP2025!ChairPersonAccess#Unlock$Key"
result2, valid_codes2 = validate_key(provided_key, required_code, codes_list_raw)

print(f"If REGISTRATION_ACCESS_CODE = {required_code}")
print(f"Valid codes set: {valid_codes2}")
print(f"Validation result: {result2}")
