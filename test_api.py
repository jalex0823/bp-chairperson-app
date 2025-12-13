#!/usr/bin/env python3
"""
Minimal test of the Flask API endpoint without database dependencies.
"""
import os
import json
from flask import Flask, jsonify, request

# Create a minimal test app
app = Flask(__name__)
app.config['REGISTRATION_ACCESS_CODE'] = 'BACKPORCH-KEY'
app.config['REGISTRATION_ACCESS_CODES'] = None

@app.route("/api/registration/validate-key", methods=["POST"])
def api_validate_registration_key():
    try:
        data = request.get_json(force=True) or {}
        provided = (data.get('key') or '').strip()
        required_code = app.config.get('REGISTRATION_ACCESS_CODE')
        codes_list_raw = app.config.get('REGISTRATION_ACCESS_CODES')
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
        return jsonify({"ok": ok})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

def test_api():
    with app.test_client() as client:
        test_cases = [
            ("BACKPORCH-KEY", True),
            ("wrong-key", False),
            ("", False),
            (" BACKPORCH-KEY ", True),
        ]
        
        for key, expected in test_cases:
            print(f"Testing key: '{key}'")
            response = client.post('/api/registration/validate-key',
                                 json={'key': key},
                                 headers={'Content-Type': 'application/json'})
            
            print(f"  Status: {response.status_code}")
            data = response.get_json()
            print(f"  Response: {data}")
            
            if response.status_code == 200 and data.get('ok') == expected:
                print(f"  ✅ Success")
            else:
                print(f"  ❌ Failed - expected ok={expected}")
            print()

if __name__ == "__main__":
    print("=== Testing Flask API Endpoint ===")
    test_api()