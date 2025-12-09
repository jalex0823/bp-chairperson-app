"""
Smoke Test Suite for BP Chairperson App
Tests all routes and basic functionality
"""

import sys
import os
from datetime import datetime, timedelta
from io import BytesIO

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set testing environment before importing app
os.environ['TESTING'] = 'True'
os.environ['SECRET_KEY'] = 'test-secret-key'
# Override database URL to use SQLite for testing
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

try:
    from app import app, db, User, Meeting
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"❌ CRITICAL: Failed to import app: {e}")
    sys.exit(1)

class SmokeTestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.client = None
        self.test_user_id = None
        self.test_admin_id = None
        self.test_meeting_id = None
        
    def setup(self):
        """Setup test client and test data"""
        print("🔧 Setting up test environment...")
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = app.test_client()
        
        # Create tables
        with app.app_context():
            try:
                db.create_all()
                print("✅ Database tables created")
                
                # Create test users
                test_user = User(
                    email='test@example.com',
                    display_name='Test User',
                    password_hash=generate_password_hash('password123'),
                    is_admin=False
                )
                db.session.add(test_user)
                
                test_admin = User(
                    email='admin@example.com',
                    display_name='Admin User',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True
                )
                db.session.add(test_admin)
                
                # Create test meeting
                test_meeting = Meeting(
                    title='Test Meeting',
                    event_date=datetime.now().date() + timedelta(days=7),
                    start_time=datetime.strptime('19:00', '%H:%M').time(),
                    meeting_type='Regular'
                )
                db.session.add(test_meeting)
                
                db.session.commit()
                
                self.test_user_id = test_user.id
                self.test_admin_id = test_admin.id
                self.test_meeting_id = test_meeting.id
                
                print(f"✅ Test data created (User ID: {self.test_user_id}, Admin ID: {self.test_admin_id}, Meeting ID: {self.test_meeting_id})")
                
            except Exception as e:
                print(f"❌ Setup failed: {e}")
                raise
    
    def test_route(self, method, path, expected_status=200, description="", login_as=None, data=None, follow_redirects=False):
        """Test a single route"""
        try:
            # Login if needed
            if login_as:
                with self.client.session_transaction() as sess:
                    sess['user_id'] = login_as
            
            # Make request
            if method == 'GET':
                response = self.client.get(path, follow_redirects=follow_redirects)
            elif method == 'POST':
                response = self.client.post(path, data=data, follow_redirects=follow_redirects)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Check status
            if response.status_code == expected_status or (expected_status == 200 and response.status_code in [200, 302]):
                self.passed += 1
                status = "✅"
            else:
                self.failed += 1
                self.errors.append(f"{method} {path}: Expected {expected_status}, got {response.status_code}")
                status = "❌"
            
            print(f"{status} {method:4} {path:50} [{response.status_code}] {description}")
            
        except Exception as e:
            self.failed += 1
            self.errors.append(f"{method} {path}: {str(e)}")
            print(f"❌ {method:4} {path:50} [ERROR] {str(e)}")
    
    def run_public_routes(self):
        """Test public routes (no login required)"""
        print("\n📋 Testing Public Routes...")
        print("-" * 100)
        
        self.test_route('GET', '/', description="Home page")
        self.test_route('GET', '/chair-resources', description="Chair resources")
        self.test_route('GET', '/host-signup-instructions', description="Host signup instructions")
        self.test_route('GET', '/registration-instructions', description="Registration instructions")
        self.test_route('GET', '/meetings/today', description="Today's meetings")
        self.test_route('GET', '/calendar', description="Calendar view")
        self.test_route('GET', '/calendar/display', description="Calendar display")
        self.test_route('GET', '/calendar/ics', description="Calendar ICS feed")
        self.test_route('GET', '/calendar.ics', description="Main calendar ICS")
        self.test_route('GET', '/calendar/export', description="Calendar export")
        self.test_route('GET', '/register', description="Registration page")
        self.test_route('GET', '/login', description="Login page")
        self.test_route('GET', '/offline', description="Offline page")
        
    def run_authenticated_routes(self):
        """Test routes requiring authentication"""
        print("\n🔐 Testing Authenticated Routes...")
        print("-" * 100)
        
        # Login first
        with app.app_context():
            self.test_route('POST', '/login', data={
                'email': 'test@example.com',
                'password': 'password123'
            }, expected_status=302, description="Login (user)")
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
        
        self.test_route('GET', '/dashboard', login_as=self.test_user_id, description="Dashboard")
        self.test_route('GET', '/profile', login_as=self.test_user_id, description="Profile page")
        self.test_route('GET', '/my-calendar.ics', login_as=self.test_user_id, description="Personal calendar ICS")
        self.test_route('GET', f'/meeting/{self.test_meeting_id}', login_as=self.test_user_id, description="Meeting detail")
        self.test_route('GET', f'/calendar/google-add/{self.test_meeting_id}', login_as=self.test_user_id, description="Google calendar add")
        self.test_route('GET', '/logout', login_as=self.test_user_id, expected_status=302, description="Logout")
    
    def run_admin_routes(self):
        """Test admin routes"""
        print("\n👑 Testing Admin Routes...")
        print("-" * 100)
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_admin_id
        
        self.test_route('GET', '/admin/meetings', login_as=self.test_admin_id, description="Admin meetings list")
        self.test_route('GET', '/admin/diagnostics', login_as=self.test_admin_id, description="Admin diagnostics")
        self.test_route('GET', '/admin/reports/chair-schedule', login_as=self.test_admin_id, description="Chair schedule report")
        self.test_route('GET', '/admin/reports/monthly', login_as=self.test_admin_id, description="Monthly report")
        self.test_route('GET', '/admin/meetings/new', login_as=self.test_admin_id, description="New meeting form")
        self.test_route('GET', f'/admin/meetings/{self.test_meeting_id}/edit', login_as=self.test_admin_id, description="Edit meeting form")
        self.test_route('GET', '/admin/analytics', login_as=self.test_admin_id, description="Analytics page")
        self.test_route('GET', '/admin/security', login_as=self.test_admin_id, description="Security page")
        self.test_route('GET', '/admin/meetings/export', login_as=self.test_admin_id, description="Export meetings")
    
    def run_api_routes(self):
        """Test API routes"""
        print("\n🔌 Testing API Routes...")
        print("-" * 100)
        
        today = datetime.now().date()
        self.test_route('GET', f'/api/day-meetings?date={today.isoformat()}', description="API: Day meetings")
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
        
        self.test_route('POST', '/api/registration/validate-key', 
                       data={'key': 'TEST123'}, 
                       description="API: Validate registration key")
    
    def run_error_handling(self):
        """Test error handling"""
        print("\n⚠️  Testing Error Handling...")
        print("-" * 100)
        
        self.test_route('GET', '/meeting/99999', expected_status=404, description="Non-existent meeting")
        self.test_route('GET', '/admin/meetings', expected_status=302, description="Admin without login (redirect)")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 100)
        print("📊 SMOKE TEST SUMMARY")
        print("=" * 100)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Total:  {self.passed + self.failed}")
        print(f"✔️  Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%" if (self.passed + self.failed) > 0 else "N/A")
        
        if self.errors:
            print(f"\n⚠️  ERRORS ({len(self.errors)}):")
            print("-" * 100)
            for error in self.errors:
                print(f"  • {error}")
        
        print("\n" + "=" * 100)
        
        return self.failed == 0
    
    def run_all_tests(self):
        """Run all smoke tests"""
        print("=" * 100)
        print("🚀 STARTING SMOKE TESTS FOR BP CHAIRPERSON APP")
        print("=" * 100)
        
        try:
            self.setup()
            
            with app.app_context():
                self.run_public_routes()
                self.run_authenticated_routes()
                self.run_admin_routes()
                self.run_api_routes()
                self.run_error_handling()
            
            success = self.print_summary()
            
            return 0 if success else 1
            
        except Exception as e:
            print(f"\n❌ FATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == '__main__':
    runner = SmokeTestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)
