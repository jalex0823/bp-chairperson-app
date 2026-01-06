"""Reset a user's password (LOCAL DB).

Usage:
  python reset_user_password.py <email> [temporary_password]

Notes:
- This updates the local database configured by your current env/DATABASE_URL.
- For Heroku/production, use heroku_reset_password.py via `heroku run`.
"""

from __future__ import annotations

import secrets
import sys

from werkzeug.security import generate_password_hash

from app import app, db, User


def generate_temp_password() -> str:
    # Avoid ambiguous characters; keep it easy to type.
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    return "BP-" + "".join(secrets.choice(alphabet) for _ in range(12))


def reset_password_local(email: str, new_password: str) -> bool:
    email = (email or "").lower().strip()
    if not email:
        print("❌ Email is required")
        return False

    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"❌ User not found in database: {email}")
            return False

        user.password_hash = generate_password_hash(new_password)
        # If the model has the flag, set it so they must change it.
        if hasattr(user, "password_reset_required"):
            user.password_reset_required = True
        db.session.commit()

        print("=" * 60)
        print("✅ PASSWORD RESET SUCCESSFUL (LOCAL)")
        print("=" * 60)
        print(f"📧 Email: {user.email}")
        print(f"👤 Display Name: {getattr(user, 'display_name', '(unknown)')}")
        print(f"🔑 Temporary Password: {new_password}")
        if hasattr(user, "password_reset_required"):
            print("⚠️  User will be required to change password on next login")
        print("=" * 60)
        print("\n⚠️  IMPORTANT:")
        print("This reset is for the LOCAL database only.")
        print("For PRODUCTION (Heroku), run:")
        print("  heroku run python heroku_reset_password.py <email> [temporary_password]")
        print("=" * 60)
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python reset_user_password.py <email> [temporary_password]")
        sys.exit(1)

    target_email = sys.argv[1]
    temp_password = sys.argv[2] if len(sys.argv) == 3 else generate_temp_password()
    ok = reset_password_local(target_email, temp_password)
    sys.exit(0 if ok else 2)
