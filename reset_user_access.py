"""Reset/unlock a user account.

Usage:
  python reset_user_access.py <email>
  python reset_user_access.py <email> --password "SomeTempPass!" 
  python reset_user_access.py <email> --unlock-only

Defaults:
- unlocks the account (clears failed attempts + lockout)
- sets a generated temporary password
- sets password_reset_required=True so the user must change it after logging in

This script is designed to work both locally and in production environments
(Heroku/DreamHost), depending on your configured DATABASE_URL / DB_* env vars.
"""

from __future__ import annotations

import argparse
import secrets
import string

from werkzeug.security import generate_password_hash

from app import app, db, User


def _generate_temp_password() -> str:
    # Friendly to type, still non-trivial.
    digits = "".join(secrets.choice(string.digits) for _ in range(6))
    return f"BP{digits}!Temp"


def reset_user_access(email: str, password: str | None, unlock_only: bool) -> int:
    normalized = (email or "").strip().lower()
    if not normalized or "@" not in normalized:
        print("❌ Please provide a valid email address")
        return 2

    with app.app_context():
        user = User.query.filter_by(email=normalized).first()
        if not user:
            print(f"❌ User not found: {normalized}")
            return 1

        # Always unlock (safe regardless of whether locked)
        user.locked_until = None
        user.failed_login_attempts = 0

        if unlock_only:
            db.session.commit()
            print("=" * 60)
            print("✅ ACCOUNT UNLOCKED")
            print("=" * 60)
            print(f"📧 Email: {user.email}")
            print(f"👤 Name:  {user.display_name}")
            print(f"🔓 locked_until: {user.locked_until}")
            print(f"🔁 failed_login_attempts: {user.failed_login_attempts}")
            print("=" * 60)
            return 0

        temp_password = password or _generate_temp_password()
        user.password_hash = generate_password_hash(temp_password)
        user.password_reset_required = True
        db.session.commit()

        print("=" * 60)
        print("✅ PASSWORD RESET + ACCOUNT UNLOCKED")
        print("=" * 60)
        print(f"📧 Email: {user.email}")
        print(f"👤 Name:  {user.display_name}")
        print(f"🔑 Temporary Password: {temp_password}")
        print("⚠️  User will be required to change password on next login")
        print(f"🔓 locked_until: {user.locked_until}")
        print(f"🔁 failed_login_attempts: {user.failed_login_attempts}")
        print("=" * 60)

        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Unlock and/or reset a user's password")
    parser.add_argument("email", help="User email")
    parser.add_argument("--password", help="Set an explicit temporary password (otherwise auto-generated)")
    parser.add_argument(
        "--unlock-only",
        action="store_true",
        help="Only unlock the account (do not change password)",
    )

    args = parser.parse_args()
    return reset_user_access(args.email, args.password, args.unlock_only)


if __name__ == "__main__":
    raise SystemExit(main())
