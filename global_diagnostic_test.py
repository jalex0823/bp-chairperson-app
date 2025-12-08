"""
Comprehensive Smoke Test for Back Porch Chair App
Tests all major functionality across the application
"""
import requests
from datetime import datetime
import sys

# Production URL
BASE_URL = "https://backporch-chair-app-35851db28c9c.herokuapp.com"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.ENDC}\n")

def print_test(name, status, message=""):
    status_color = Colors.GREEN if status else Colors.RED
    status_text = "✓ PASS" if status else "✗ FAIL"
    print(f"{status_color}{status_text}{Colors.ENDC} | {name}")
    if message:
        print(f"         {Colors.YELLOW}{message}{Colors.ENDC}")

def test_public_pages():
    """Test all publicly accessible pages"""
    print_header("PUBLIC PAGES TEST")
    
    tests = [
        ("/", "Home/Index Page"),
        ("/login", "Login Page"),
        ("/register", "Registration Page"),
        ("/chair-resources", "Chair Resources Page"),
        ("/meetings/today", "Today's Meetings Page"),
    ]
    
    passed = 0
    total = len(tests)
    
    for path, name in tests:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
            success = response.status_code == 200
            print_test(name, success, f"Status: {response.status_code}")
            if success:
                passed += 1
        except Exception as e:
            print_test(name, False, f"Error: {str(e)}")
    
    return passed, total

def test_authenticated_redirects():
    """Test that protected pages redirect to login"""
    print_header("AUTHENTICATION PROTECTION TEST")
    
    tests = [
        ("/dashboard", "Dashboard"),
        ("/profile", "Profile Page"),
        ("/calendar", "Calendar Page"),
        ("/admin/meetings", "Admin Meetings"),
    ]
    
    passed = 0
    total = len(tests)
    
    for path, name in tests:
        try:
            response = requests.get(f"{BASE_URL}{path}", allow_redirects=False, timeout=10)
            # Should redirect to login (302) or show unauthorized (401/403)
            success = response.status_code in [302, 401, 403]
            print_test(name, success, f"Status: {response.status_code} (Protected)")
            if success:
                passed += 1
        except Exception as e:
            print_test(name, False, f"Error: {str(e)}")
    
    return passed, total

def test_api_endpoints():
    """Test API endpoints"""
    print_header("API ENDPOINTS TEST")
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    tests = [
        (f"/api/day-meetings?date={today}", "Day Meetings API"),
        (f"/api/week-meetings?start={today}&end={today}", "Week Meetings API"),
    ]
    
    passed = 0
    total = len(tests)
    
    for path, name in tests:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
            success = response.status_code == 200
            if success:
                try:
                    data = response.json()
                    print_test(name, True, f"Status: {response.status_code}, Data: Valid JSON")
                    passed += 1
                except:
                    print_test(name, False, "Invalid JSON response")
            else:
                print_test(name, False, f"Status: {response.status_code}")
        except Exception as e:
            print_test(name, False, f"Error: {str(e)}")
    
    return passed, total

def test_static_assets():
    """Test static assets are loading"""
    print_header("STATIC ASSETS TEST")
    
    tests = [
        ("/static/css/custom.css", "Custom CSS"),
        ("/static/js/meeting-enhancements.js", "Meeting Enhancements JS"),
        ("/static/manifest.json", "PWA Manifest"),
        ("/static/sw.js", "Service Worker"),
    ]
    
    passed = 0
    total = len(tests)
    
    for path, name in tests:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
            success = response.status_code == 200
            print_test(name, success, f"Status: {response.status_code}")
            if success:
                passed += 1
        except Exception as e:
            print_test(name, False, f"Error: {str(e)}")
    
    return passed, total

def test_response_times():
    """Test response times for key pages"""
    print_header("PERFORMANCE TEST")
    
    tests = [
        ("/", "Home Page"),
        ("/login", "Login Page"),
        ("/meetings/today", "Today's Meetings"),
        ("/chair-resources", "Chair Resources"),
    ]
    
    passed = 0
    total = len(tests)
    
    for path, name in tests:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
            response_time = response.elapsed.total_seconds()
            # Pass if response time is under 3 seconds
            success = response_time < 3.0
            print_test(
                name, 
                success, 
                f"Response time: {response_time:.2f}s {'(Good)' if response_time < 1 else '(Acceptable)' if response_time < 3 else '(Slow)'}"
            )
            if success:
                passed += 1
        except Exception as e:
            print_test(name, False, f"Error: {str(e)}")
    
    return passed, total

def test_database_connectivity():
    """Test database is responding"""
    print_header("DATABASE CONNECTIVITY TEST")
    
    try:
        # Test today's meetings which requires DB
        response = requests.get(f"{BASE_URL}/meetings/today", timeout=10)
        success = response.status_code == 200 and len(response.content) > 0
        print_test("Database Query (Today's Meetings)", success, f"Status: {response.status_code}")
        return (1 if success else 0, 1)
    except Exception as e:
        print_test("Database Query", False, f"Error: {str(e)}")
        return (0, 1)

def test_error_handling():
    """Test error pages"""
    print_header("ERROR HANDLING TEST")
    
    tests = [
        ("/nonexistent-page-12345", "404 Not Found", [404]),
        ("/api/day-meetings?date=invalid", "Invalid API Parameter", [400, 500]),
    ]
    
    passed = 0
    total = len(tests)
    
    for path, name, expected_codes in tests:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
            success = response.status_code in expected_codes
            print_test(name, success, f"Status: {response.status_code} (Expected: {expected_codes})")
            if success:
                passed += 1
        except Exception as e:
            print_test(name, False, f"Error: {str(e)}")
    
    return passed, total

def test_security_headers():
    """Test security headers"""
    print_header("SECURITY HEADERS TEST")
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        headers = response.headers
        
        tests = [
            ("X-Frame-Options" in headers or "Content-Security-Policy" in headers, "Clickjacking Protection"),
            ("X-Content-Type-Options" in headers, "MIME Sniffing Protection"),
        ]
        
        passed = sum(1 for result, _ in tests if result)
        total = len(tests)
        
        for result, name in tests:
            print_test(name, result)
        
        return passed, total
    except Exception as e:
        print_test("Security Headers Check", False, f"Error: {str(e)}")
        return (0, 2)

def main():
    print(f"\n{Colors.BOLD}{'*' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}COMPREHENSIVE SMOKE TEST - BACK PORCH CHAIR APP{Colors.ENDC}".center(80))
    print(f"{Colors.BOLD}Environment: PRODUCTION{Colors.ENDC}".center(80))
    print(f"{Colors.BOLD}URL: {BASE_URL}{Colors.ENDC}".center(80))
    print(f"{Colors.BOLD}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}".center(80))
    print(f"{Colors.BOLD}{'*' * 80}{Colors.ENDC}\n")
    
    all_results = []
    
    # Run all test suites
    all_results.append(test_public_pages())
    all_results.append(test_authenticated_redirects())
    all_results.append(test_api_endpoints())
    all_results.append(test_static_assets())
    all_results.append(test_response_times())
    all_results.append(test_database_connectivity())
    all_results.append(test_error_handling())
    all_results.append(test_security_headers())
    
    # Calculate totals
    total_passed = sum(passed for passed, _ in all_results)
    total_tests = sum(total for _, total in all_results)
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"{Colors.BOLD}Total Tests Run:{Colors.ENDC} {total_tests}")
    print(f"{Colors.GREEN}{Colors.BOLD}Tests Passed:{Colors.ENDC} {total_passed}")
    print(f"{Colors.RED}{Colors.BOLD}Tests Failed:{Colors.ENDC} {total_tests - total_passed}")
    print(f"{Colors.BOLD}Success Rate:{Colors.ENDC} {success_rate:.1f}%\n")
    
    if success_rate >= 90:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ APPLICATION STATUS: HEALTHY{Colors.ENDC}")
    elif success_rate >= 70:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ APPLICATION STATUS: NEEDS ATTENTION{Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ APPLICATION STATUS: CRITICAL ISSUES{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}{'*' * 80}{Colors.ENDC}\n")
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 90 else 1)

if __name__ == "__main__":
    main()
