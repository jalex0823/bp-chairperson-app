"""Promote a chairperson user to admin and set a new password.

Usage (local DB):
  python make_admin_and_reset_password.py "<email_or_display_name>" "<new_password>"

Usage (Heroku/production):
  heroku run python make_admin_and_reset_password.py "<email_or_display_name>" "<new_password>"

Notes:
- This ONLY affects chairperson accounts (User table). Sponsor accounts are independent.
- If you pass a display name and multiple users match, the script will abort and list candidates.
"""

from __future__ import annotations

import sys

from werkzeug.security import generate_password_hash

from app import app, db, User


def _is_email(value: str) -> bool:
    return "@" in (value or "")


def promote_and_reset(identifier: str, new_password: str) -> bool:
    ident = (identifier or "").strip()
    if not ident:
        print("❌ Identifier is required (email or display name).")
        return False
    if not new_password:
        print("❌ New password is required.")
        return False

    with app.app_context():
        if _is_email(ident):
            email = ident.lower().strip()
            matches = User.query.filter_by(email=email).all()
        else:
            # Case-insensitive exact match on display name
            matches = User.query.filter(User.display_name.ilike(ident)).all()

        if not matches:
            print(f"❌ No user found for: {ident}")
            return False

        if len(matches) > 1:
            print("❌ Multiple users matched that display name. Re-run using the email.")
            print("Candidates:")
            for u in matches:
                print(f" - {u.display_name} <{u.email}>  (BP-{1000 + u.id})")
            return False

        user = matches[0]

        user.is_admin = True
        user.password_hash = generate_password_hash(new_password)

        # If present, ensure they can log in immediately.
        if hasattr(user, "password_reset_required"):
            user.password_reset_required = False
        if hasattr(user, "failed_login_attempts"):
            user.failed_login_attempts = 0
        if hasattr(user, "locked_until"):
            user.locked_until = None

        db.session.commit()

        print("=" * 60)
        print("✅ USER UPDATED")
        print("=" * 60)
        print(f"👤 Display Name: {getattr(user, 'display_name', '(unknown)')}")
        print(f"📧 Email: {user.email}")
        print(f"🛡️  is_admin: {user.is_admin}")
        print("🔑 Password updated.")
        print("=" * 60)
        return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: python make_admin_and_reset_password.py "<email_or_display_name>" "<new_password>"')
        sys.exit(1)

    ok = promote_and_reset(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 2)

