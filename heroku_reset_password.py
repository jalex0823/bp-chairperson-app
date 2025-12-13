"""Reset password for any user - Run on Heroku with: heroku run python heroku_reset_password.py"""
from app import app, db, User
from werkzeug.security import generate_password_hash
import sys

def reset_password(email, new_password):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ User {email} not found")
            return False
        
        user.password_hash = generate_password_hash(new_password)
        user.password_reset_required = True  # Force password change on next login
        db.session.commit()
        
        print("="*60)
        print("✅ PASSWORD RESET SUCCESSFUL")
        print("="*60)
        print(f"📧 Email: {user.email}")
        print(f"👤 Display Name: {user.display_name}")
        print(f"🔑 Temporary Password: {new_password}")
        print("⚠️  User will be required to change password on next login")
        print("="*60)
        return True

if __name__ == "__main__":
    # Reset password for rblwood@comcast.net
    email = "rblwood@comcast.net"
    new_password = "BackPorch2025!"
    
    print(f"\n🔄 Resetting password for {email}...")
    reset_password(email, new_password)
