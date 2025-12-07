"""
Comprehensive smoke test for all app routes and functionality.
Tests public endpoints, authenticated endpoints, and API endpoints.
"""
import requests
import time
import sys

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 10

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def test_endpoint(method, path, expected_status=200, data=None, json_data=None, description=""):
    """Test a single endpoint."""
    url = BASE_URL + path
    try:
        if method.upper() == "GET":
            resp = requests.get(url, timeout=TIMEOUT)
        elif method.upper() == "POST":
            resp = requests.post(url, data=data, json=json_data, timeout=TIMEOUT)
        else:
            return False, f"Unsupported method: {method}"
        
        status = resp.status_code
        success = status == expected_status or (expected_status == 200 and status in [200, 302, 401])
        
        return success, f"{status} - {description or path}"
    except requests.RequestException as e:
        return False, f"ERROR - {str(e)[:50]}"

def run_smoke_tests():
    """Run comprehensive smoke tests."""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}COMPREHENSIVE SMOKE TEST - Back Porch Chairperson App{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    tests = []
    
    # Public Pages
    print(f"{Colors.YELLOW}PUBLIC PAGES{Colors.END}")
    public_tests = [
        ("GET", "/", 200, "Homepage"),
        ("GET", "/calendar", 200, "Calendar view"),
        ("GET", "/calendar/display", 200, "Calendar display"),
        ("GET", "/meetings/today", 200, "Today's meetings"),
        ("GET", "/chair-resources", 200, "Chair resources"),
        ("GET", "/login", 200, "Login page"),
        ("GET", "/register", 200, "Registration page"),
    ]
    
    for method, path, expected, desc in public_tests:
        success, msg = test_endpoint(method, path, expected, description=desc)
        tests.append((desc, success, msg))
        icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
        print(f"  {icon} {desc}: {msg}")
    
    # Calendar Exports
    print(f"\n{Colors.YELLOW}CALENDAR EXPORTS{Colors.END}")
    export_tests = [
        ("GET", "/calendar.ics", 200, "Full calendar ICS export"),
        ("GET", "/calendar/2025/12.ics", 200, "Monthly ICS export"),
    ]
    
    for method, path, expected, desc in export_tests:
        success, msg = test_endpoint(method, path, expected, description=desc)
        tests.append((desc, success, msg))
        icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
        print(f"  {icon} {desc}: {msg}")
    
    # Static Assets
    print(f"\n{Colors.YELLOW}STATIC ASSETS{Colors.END}")
    static_tests = [
        ("GET", "/static/img/favicon.ico", 200, "Favicon"),
        ("GET", "/static/img/favicon-16x16.png", 200, "Favicon 16x16"),
        ("GET", "/static/img/favicon-32x32.png", 200, "Favicon 32x32"),
        ("GET", "/static/css/custom.css", 200, "Custom CSS"),
        ("GET", "/static/manifest.json", 200, "PWA Manifest"),
        ("GET", "/static/sw.js", 200, "Service Worker"),
    ]
    
    for method, path, expected, desc in static_tests:
        success, msg = test_endpoint(method, path, expected, description=desc)
        tests.append((desc, success, msg))
        icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
        print(f"  {icon} {desc}: {msg}")
    
    # API Endpoints
    print(f"\n{Colors.YELLOW}API ENDPOINTS{Colors.END}")
    api_tests = [
        ("POST", "/api/registration/validate-key", 200, "Registration key validation"),
    ]
    
    # Test registration key validation with valid and invalid keys
    success, msg = test_endpoint("POST", "/api/registration/validate-key", 200, 
                                 json_data={"key": "BP2025!ChairPersonAccess#Unlock$Key"},
                                 description="Valid registration key")
    tests.append(("Valid registration key", success, msg))
    icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
    print(f"  {icon} Valid registration key: {msg}")
    
    success, msg = test_endpoint("POST", "/api/registration/validate-key", 200,
                                 json_data={"key": "invalid-key"},
                                 description="Invalid registration key")
    tests.append(("Invalid registration key", success, msg))
    icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
    print(f"  {icon} Invalid registration key: {msg}")
    
    # Protected Pages (should redirect or show 401/302)
    print(f"\n{Colors.YELLOW}PROTECTED PAGES (Expecting Redirect/Auth){Colors.END}")
    protected_tests = [
        ("GET", "/dashboard", 302, "User dashboard"),
        ("GET", "/profile", 302, "User profile"),
        ("GET", "/admin/meetings", 302, "Admin meetings"),
        ("GET", "/admin/analytics", 302, "Admin analytics"),
        ("GET", "/admin/diagnostics", 302, "Admin diagnostics"),
        ("GET", "/admin/security", 302, "Admin security"),
    ]
    
    for method, path, expected, desc in protected_tests:
        success, msg = test_endpoint(method, path, expected, description=desc)
        tests.append((desc, success, msg))
        # For protected pages, 302 (redirect) is expected and good
        if "302" in msg or "401" in msg:
            icon = f"{Colors.GREEN}✓{Colors.END}"
            success = True
        else:
            icon = f"{Colors.YELLOW}?{Colors.END}"
        print(f"  {icon} {desc}: {msg}")
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    total = len(tests)
    passed = sum(1 for _, success, _ in tests if success)
    failed = total - passed
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"{Colors.BLUE}SUMMARY{Colors.END}")
    print(f"  Total Tests: {total}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"  {Colors.RED}Failed: {failed}{Colors.END}")
    print(f"  Success Rate: {pass_rate:.1f}%")
    
    if failed > 0:
        print(f"\n{Colors.RED}FAILED TESTS:{Colors.END}")
        for desc, success, msg in tests:
            if not success:
                print(f"  {Colors.RED}✗{Colors.END} {desc}: {msg}")
    
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    return failed == 0

if __name__ == "__main__":
    print("\nWaiting 2 seconds for server to be ready...")
    time.sleep(2)
    
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
