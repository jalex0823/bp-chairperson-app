"""
Unlock a user account that has been locked due to failed login attempts.
Usage: python unlock_account.py <email>
"""
import sys
import os

# Set up the app context
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', '')
from app import app, db, User

def unlock_user_account(email):
    """Unlock a user account by email."""
    with app.app_context():
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        if not user.is_locked():
            print(f"ℹ️  Account {email} is not locked.")
            print(f"   Failed attempts: {user.failed_login_attempts}")
            return True
        
        # Unlock the account
        user.unlock_account()
        
        print(f"✅ Account unlocked: {email}")
        print(f"   Name: {user.display_name}")
        print(f"   Failed attempts reset to 0")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python unlock_account.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    success = unlock_user_account(email)
    sys.exit(0 if success else 1)
