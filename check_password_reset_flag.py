"""
Check and set password_reset_required flag for a user.
Usage: python check_password_reset_flag.py <email>
"""
import sys
import os

# Set up the app context
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', '')
from app import app, db, User

def check_and_set_flag(email):
    """Check and set password_reset_required flag."""
    with app.app_context():
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        print(f"User: {user.display_name} ({user.email})")
        print(f"Current password_reset_required: {user.password_reset_required}")
        
        if not user.password_reset_required:
            print(f"\n⚠️  Setting password_reset_required to True...")
            user.password_reset_required = True
            db.session.commit()
            print(f"✅ Flag set! User will be prompted to change password on next login.")
        else:
            print(f"✅ Flag is already set correctly.")
        
        return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_password_reset_flag.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    success = check_and_set_flag(email)
    sys.exit(0 if success else 1)
