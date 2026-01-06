"""Reset password for any user (PRODUCTION / Heroku).

Usage:
    heroku run python heroku_reset_password.py <email> [temporary_password]
"""

from __future__ import annotations

import secrets
import sys

from werkzeug.security import generate_password_hash

from app import app, db, User


def generate_temp_password() -> str:
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
        return "BP-" + "".join(secrets.choice(alphabet) for _ in range(12))

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
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python heroku_reset_password.py <email> [temporary_password]")
        sys.exit(1)

    email = sys.argv[1]
    new_password = sys.argv[2] if len(sys.argv) == 3 else generate_temp_password()

    print(f"\n🔄 Resetting password for {email}...")
    ok = reset_password(email, new_password)
    sys.exit(0 if ok else 2)
