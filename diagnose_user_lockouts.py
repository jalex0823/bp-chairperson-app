"""Diagnose repeated login lockouts for a specific user.

Usage:
  python diagnose_user_lockouts.py <email>
  python diagnose_user_lockouts.py <email> --days 30 --limit 200
  python diagnose_user_lockouts.py <email> --actions account_locked,login_failure,login_attempt_locked_account

Prints:
- current lockout status (failed attempts, locked_until)
- recent audit log events related to login/lockout

This is intended for admins/support to understand WHY an account keeps locking:
- repeated bad passwords
- mobile autofill adding whitespace
- attempts coming from unexpected IPs/devices
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from app import app, db, User, AuditLog


DEFAULT_ACTIONS = [
    "account_locked",
    "login_failure",
    "login_attempt_locked_account",
    "login_success",
    "password_changed",
]


def _normalize_email(raw: str) -> str:
    return (raw or "").strip().lower()


def _as_dict(details):
    if details is None:
        return {}
    if isinstance(details, dict):
        return details
    # Some DBs/drivers might give a JSON string; best-effort.
    try:
        import json

        if isinstance(details, str) and details.strip():
            parsed = json.loads(details)
            return parsed if isinstance(parsed, dict) else {}
    except Exception:
        pass
    return {}


def _fmt_dt(dt) -> str:
    if not dt:
        return "-"
    try:
        # AuditLog.created_at is stored with timezone; normalize to ISO.
        if getattr(dt, "tzinfo", None) is None:
            return dt.replace(tzinfo=timezone.utc).isoformat()
        return dt.isoformat()
    except Exception:
        return str(dt)


def diagnose(email: str, days: int, limit: int, actions: list[str]) -> int:
    normalized = _normalize_email(email)
    if not normalized or "@" not in normalized:
        print("❌ Please provide a valid email address")
        return 2

    since = datetime.now(timezone.utc) - timedelta(days=max(0, days))

    with app.app_context():
        user = User.query.filter_by(email=normalized).first()
        if not user:
            print(f"❌ User not found: {normalized}")
            return 1

        print("=" * 80)
        print("USER STATUS")
        print("=" * 80)
        print(f"Email:              {user.email}")
        print(f"Name:               {user.display_name}")
        print(f"User ID:             {user.id}")
        print(f"Last login:          {_fmt_dt(user.last_login)}")
        print(f"Failed attempts:     {user.failed_login_attempts}")
        print(f"Locked until:        {_fmt_dt(user.locked_until)}")
        print(f"Is locked now:       {bool(user.is_locked())}")
        print(f"Reset required flag: {bool(user.password_reset_required)}")

        q = AuditLog.query.filter(
            AuditLog.user_id == user.id,
            AuditLog.created_at >= since,
        )
        if actions:
            q = q.filter(AuditLog.action.in_(actions))

        events = q.order_by(AuditLog.created_at.desc()).limit(limit).all()

        print("\n" + "=" * 80)
        print(f"RECENT AUDIT EVENTS (since {_fmt_dt(since)}; showing {len(events)} of {limit})")
        print("=" * 80)

        if not events:
            print("(no matching events)")
            return 0

        for ev in events:
            details = _as_dict(ev.details)
            failed_attempts = details.get("failed_attempts")
            pwd_ws = details.get("password_had_outer_whitespace")
            pwd_len = details.get("password_length")

            summary_bits = []
            if failed_attempts is not None:
                summary_bits.append(f"failed_attempts={failed_attempts}")
            if pwd_ws is not None:
                summary_bits.append(f"outer_whitespace={pwd_ws}")
            if pwd_len is not None:
                summary_bits.append(f"pw_len={pwd_len}")

            summary = ("; ".join(summary_bits)) if summary_bits else ""

            ua = (ev.user_agent or "").replace("\n", " ").strip()
            if len(ua) > 120:
                ua = ua[:117] + "..."

            print(
                f"{_fmt_dt(ev.created_at)} | {ev.action} | ip={ev.ip_address or '-'} | ua={ua or '-'}"
                + (f" | {summary}" if summary else "")
            )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose user login lockouts via audit logs")
    parser.add_argument("email", help="User email")
    parser.add_argument("--days", type=int, default=14, help="How many days back to search (default: 14)")
    parser.add_argument("--limit", type=int, default=100, help="Max audit events to print (default: 100)")
    parser.add_argument(
        "--actions",
        default=",".join(DEFAULT_ACTIONS),
        help=f"Comma-separated audit actions to include (default: {','.join(DEFAULT_ACTIONS)})",
    )

    args = parser.parse_args()
    actions = [a.strip() for a in (args.actions or "").split(",") if a.strip()]
    return diagnose(args.email, args.days, args.limit, actions)


if __name__ == "__main__":
    raise SystemExit(main())
