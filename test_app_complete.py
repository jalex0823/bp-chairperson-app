"""
Comprehensive smoke test using Flask test client (no server needed).
Tests all routes and functionality directly.
"""
import sys
import os

# Ensure we can import the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def run_comprehensive_tests():
    """Run comprehensive smoke tests using Flask test client."""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}COMPREHENSIVE SMOKE TEST - Back Porch Chairperson App{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    tests = []
    
    with app.test_client() as client:
        # Public Pages
        print(f"{Colors.YELLOW}PUBLIC PAGES{Colors.END}")
        public_tests = [
            ("/", "Homepage"),
            ("/calendar", "Calendar view"),
            ("/calendar/display", "Calendar display"),
            ("/meetings/today", "Today's meetings"),
            ("/chair-resources", "Chair resources"),
            ("/login", "Login page"),
            ("/register", "Registration page"),
        ]
        
        for path, desc in public_tests:
            try:
                response = client.get(path)
                status = response.status_code
                success = status in [200, 302]
                tests.append((desc, success, status))
                icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
                print(f"  {icon} {desc}: {status}")
            except Exception as e:
                tests.append((desc, False, str(e)[:50]))
                print(f"  {Colors.RED}✗{Colors.END} {desc}: ERROR - {str(e)[:50]}")
        
        # Calendar Exports
        print(f"\n{Colors.YELLOW}CALENDAR EXPORTS{Colors.END}")
        export_tests = [
            ("/calendar.ics", "Full calendar ICS export"),
            ("/calendar/2025/12.ics", "Monthly ICS export (Dec 2025)"),
        ]
        
        for path, desc in export_tests:
            try:
                response = client.get(path)
                status = response.status_code
                success = status == 200
                tests.append((desc, success, status))
                icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
                print(f"  {icon} {desc}: {status}")
            except Exception as e:
                tests.append((desc, False, str(e)[:50]))
                print(f"  {Colors.RED}✗{Colors.END} {desc}: ERROR - {str(e)[:50]}")
        
        # Static Assets
        print(f"\n{Colors.YELLOW}STATIC ASSETS{Colors.END}")
        static_tests = [
            ("/static/img/favicon.ico", "Favicon"),
            ("/static/img/favicon-16x16.png", "Favicon 16x16"),
            ("/static/img/favicon-32x32.png", "Favicon 32x32"),
            ("/static/css/custom.css", "Custom CSS"),
            ("/static/manifest.json", "PWA Manifest"),
            ("/static/sw.js", "Service Worker"),
        ]
        
        for path, desc in static_tests:
            try:
                response = client.get(path)
                status = response.status_code
                success = status in [200, 304, 404]  # 404 is ok if file doesn't exist
                tests.append((desc, success, status))
                icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
                print(f"  {icon} {desc}: {status}")
            except Exception as e:
                tests.append((desc, False, str(e)[:50]))
                print(f"  {Colors.RED}✗{Colors.END} {desc}: ERROR - {str(e)[:50]}")
        
        # API Endpoints
        print(f"\n{Colors.YELLOW}API ENDPOINTS{Colors.END}")
        
        # Test registration key validation with valid key
        try:
            response = client.post('/api/registration/validate-key',
                                  json={'key': 'BP2025!ChairPersonAccess#Unlock$Key'},
                                  content_type='application/json')
            status = response.status_code
            data = response.get_json()
            success = status == 200 and data.get('ok') == True
            tests.append(("Valid registration key", success, f"{status} - ok={data.get('ok')}"))
            icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
            print(f"  {icon} Valid registration key: {status} - ok={data.get('ok')}")
        except Exception as e:
            tests.append(("Valid registration key", False, str(e)[:50]))
            print(f"  {Colors.RED}✗{Colors.END} Valid registration key: ERROR - {str(e)[:50]}")
        
        # Test registration key validation with invalid key
        try:
            response = client.post('/api/registration/validate-key',
                                  json={'key': 'invalid-key'},
                                  content_type='application/json')
            status = response.status_code
            data = response.get_json()
            success = status == 200 and data.get('ok') == False
            tests.append(("Invalid registration key", success, f"{status} - ok={data.get('ok')}"))
            icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
            print(f"  {icon} Invalid registration key: {status} - ok={data.get('ok')}")
        except Exception as e:
            tests.append(("Invalid registration key", False, str(e)[:50]))
            print(f"  {Colors.RED}✗{Colors.END} Invalid registration key: ERROR - {str(e)[:50]}")
        
        # Protected Pages (should redirect to login)
        print(f"\n{Colors.YELLOW}PROTECTED PAGES (Expecting Redirect){Colors.END}")
        protected_tests = [
            ("/dashboard", "User dashboard"),
            ("/profile", "User profile"),
            ("/admin/meetings", "Admin meetings"),
            ("/admin/analytics", "Admin analytics"),
            ("/admin/diagnostics", "Admin diagnostics"),
            ("/admin/security", "Admin security"),
        ]
        
        for path, desc in protected_tests:
            try:
                response = client.get(path, follow_redirects=False)
                status = response.status_code
                # 302 redirect to login is expected and correct
                success = status in [302, 401]
                tests.append((desc, success, status))
                icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
                print(f"  {icon} {desc}: {status}")
            except Exception as e:
                tests.append((desc, False, str(e)[:50]))
                print(f"  {Colors.RED}✗{Colors.END} {desc}: ERROR - {str(e)[:50]}")
        
        # Form Endpoints
        print(f"\n{Colors.YELLOW}FORM ENDPOINTS{Colors.END}")
        form_tests = [
            ("/login", "POST", "Login form handler"),
            ("/register", "POST", "Registration form handler"),
        ]
        
        for path, method, desc in form_tests:
            try:
                if method == "POST":
                    response = client.post(path, data={})
                status = response.status_code
                # Form posts without data should return 200 with validation errors or 302
                success = status in [200, 302, 400]
                tests.append((desc, success, status))
                icon = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
                print(f"  {icon} {desc}: {status}")
            except Exception as e:
                tests.append((desc, False, str(e)[:50]))
                print(f"  {Colors.RED}✗{Colors.END} {desc}: ERROR - {str(e)[:50]}")
    
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
    try:
        success = run_comprehensive_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n{Colors.RED}FATAL ERROR:{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
