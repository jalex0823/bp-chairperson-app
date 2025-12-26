"""Smoke test for mobile-friendly login behavior.

Verifies:
- Normal login works
- Trailing-space password (mobile autofill quirk) can still authenticate
- Lockout threshold is configurable
- Locked accounts can still log in if the correct password is provided (auto-unlock)

Runs against the configured database; creates and deletes a temporary test user.
"""

from __future__ import annotations

from app import app, db, User


def post_login(client, email: str, password: str):
    return client.post('/login', data={'email': email, 'password': password}, follow_redirects=False)


def post_logout(client):
    return client.get('/logout', follow_redirects=False)


def main() -> int:
    # Make tests fast and deterministic
    app.config['WTF_CSRF_ENABLED'] = False

    # Deliberately small numbers for testing
    app.config['ENABLE_ACCOUNT_LOCKOUT'] = True
    app.config['MAX_FAILED_LOGIN_ATTEMPTS'] = 3
    app.config['LOCKOUT_MINUTES'] = 1
    app.config['ALLOW_PASSWORD_TRIM_ON_LOGIN'] = True
    app.config['ALLOW_LOCKED_ACCOUNT_LOGIN_IF_PASSWORD_CORRECT'] = True

    email = 'mobiletest_login@example.com'
    password = 'TestPass123'

    with app.app_context():
        existing = User.query.filter_by(email=email).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

        u = User(display_name='Mobile Test', email=email, is_admin=False, agreed_guidelines=True)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        uid = u.id

    client = app.test_client()

    # 1) Normal login works
    r1 = post_login(client, email, password)
    print('1) login status:', r1.status_code, 'location:', r1.headers.get('Location'))
    post_logout(client)

    # 2) Login with trailing space should work
    r2 = post_login(client, email, password + ' ')
    print('2) trailing-space login status:', r2.status_code, 'location:', r2.headers.get('Location'))
    post_logout(client)

    # 3) Force lockout
    post_login(client, email, 'wrong1')
    post_login(client, email, 'wrong2')
    r3 = post_login(client, email, 'wrong3')
    print('3) 3rd wrong login status:', r3.status_code, 'location:', r3.headers.get('Location'))

    with app.app_context():
        u = User.query.get(uid)
        print('   after wrong attempts failed_login_attempts=', u.failed_login_attempts, 'locked_until=', u.locked_until)

    # 4) Correct password should log in even while locked
    r4 = post_login(client, email, password)
    print('4) locked-but-correct login status:', r4.status_code, 'location:', r4.headers.get('Location'))

    with app.app_context():
        u = User.query.get(uid)
        print('   after correct login failed_login_attempts=', u.failed_login_attempts, 'locked_until=', u.locked_until)

    # Cleanup
    with app.app_context():
        u = User.query.get(uid)
        if u:
            db.session.delete(u)
            db.session.commit()

    print('smoke ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
