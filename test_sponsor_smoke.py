"""
Sponsor Smoke Test (local)

Covers the sponsor flow end-to-end using Flask test client:
- Sponsor registration (key-gated)
- Sponsor login
- Sponsor portal update (including profile image upload)
- Sponsor image route returns correct mimetype
- Sponsor portal can remove profile image
- Sponsor can delete account (and associated data)
"""

from __future__ import annotations

import os
import sys
import tempfile
from io import BytesIO


def _fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def run() -> int:
    # Configure env BEFORE importing app/config
    test_db_path = os.path.join(tempfile.gettempdir(), "bp_sponsor_smoke.db")
    os.environ["TESTING"] = "True"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"
    os.environ["SPONSOR_REGISTRATION_ACCESS_CODE"] = "BP-SPONSOR-TEST-1234"
    os.environ["SEND_REGISTRATION_CONFIRMATION_TO_USER"] = "False"

    try:
        from app import app, db, Sponsor, SponsorAccount  # noqa
    except Exception as e:
        return _fail(f"Import app failed: {e}")

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    # Ensure fresh DB
    try:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    except Exception:
        pass

    with app.app_context():
        db.create_all()

    client = app.test_client()

    sponsor_email = "sponsor_smoke@example.com"
    sponsor_password = "SponsorPass123!"

    # 1) Sponsor registration (key gated)
    bio = "I am available to sponsor and can meet weekly. Call or email me."
    if len(bio) < 40:
        bio = bio + ("." * (40 - len(bio)))

    reg_data = {
        "access_code": "BP-SPONSOR-TEST-1234",
        "display_name": "Sponsor Smoke",
        "email": sponsor_email,
        "password": sponsor_password,
        "sobriety_date": "2020-01-01",
        "current_sponsees": "0",
        "max_sponsees": "1",
        "phone": "8323417193",
        "bio": bio,
    }

    png_bytes = b"\x89PNG\r\n\x1a\n" + (b"\x00" * 128)
    reg_data_with_file = dict(reg_data)
    reg_data_with_file["profile_image"] = (BytesIO(png_bytes), "bio.png")

    resp = client.post(
        "/sponsor-register",
        data=reg_data_with_file,
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    if resp.status_code != 302:
        body = resp.get_data(as_text=True)[:5000]
        return _fail(f"Registration expected 302, got {resp.status_code}. Body snippet:\n{body}")

    # 2) Sponsor login
    resp = client.post(
        "/sponsor/login",
        data={"email": sponsor_email, "password": sponsor_password},
        follow_redirects=False,
    )
    if resp.status_code != 302:
        body = resp.get_data(as_text=True)[:5000]
        return _fail(f"Login expected 302, got {resp.status_code}. Body snippet:\n{body}")

    # 3) Sponsor portal loads (logged in)
    resp = client.get("/sponsor/portal")
    if resp.status_code != 200:
        return _fail(f"Portal expected 200, got {resp.status_code}")
    html = resp.get_data(as_text=True)
    if "Sponsor Portal" not in html or "Danger zone" not in html:
        return _fail("Portal HTML missing expected content (Sponsor Portal/Danger zone)")

    # Find sponsor id
    with app.app_context():
        acct = SponsorAccount.query.filter_by(email=sponsor_email).first()
        if not acct:
            return _fail("SponsorAccount not found after registration")
        sponsor_id = acct.sponsor_id

    # 4) Sponsor image route returns PNG (from registration upload)
    resp = client.get(f"/sponsor/image/{sponsor_id}")
    if resp.status_code != 200:
        return _fail(f"Sponsor image expected 200, got {resp.status_code}")
    if not (resp.mimetype == "image/png"):
        return _fail(f"Sponsor image mimetype expected image/png, got {resp.mimetype}")

    # 5) Update portal with a new photo (webp header) and verify mimetype
    update_bio = bio + " Updated."
    webp_bytes = b"RIFF" + (b"\x00" * 4) + b"WEBP" + (b"\x00" * 64)
    update_data = {
        "current_sponsees": "0",
        "max_sponsees": "2",
        "email": sponsor_email,
        "phone": "(832) 341-7193",
        "bio": update_bio,
        "is_active": "y",
        "profile_image": (BytesIO(webp_bytes), "bio.webp"),
    }

    resp = client.post(
        "/sponsor/portal",
        data=update_data,
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    if resp.status_code != 302:
        body = resp.get_data(as_text=True)[:5000]
        return _fail(f"Portal update expected 302, got {resp.status_code}. Body snippet:\n{body}")

    resp = client.get(f"/sponsor/image/{sponsor_id}")
    if resp.status_code != 200:
        return _fail(f"Sponsor image (after update) expected 200, got {resp.status_code}")
    if resp.mimetype != "image/webp":
        return _fail(f"Sponsor image mimetype expected image/webp, got {resp.mimetype}")

    # 6) Remove profile image
    remove_data = {
        "current_sponsees": "0",
        "max_sponsees": "2",
        "email": sponsor_email,
        "phone": "(832) 341-7193",
        "bio": update_bio,
        "is_active": "y",
        "remove_profile_image": "y",
    }
    resp = client.post("/sponsor/portal", data=remove_data, follow_redirects=False)
    if resp.status_code != 302:
        body = resp.get_data(as_text=True)[:5000]
        return _fail(f"Portal remove-photo expected 302, got {resp.status_code}. Body snippet:\n{body}")

    resp = client.get(f"/sponsor/image/{sponsor_id}")
    if resp.status_code != 404:
        return _fail(f"Sponsor image after removal expected 404, got {resp.status_code}")

    # 7) Delete sponsor account (requires password)
    resp = client.post(
        "/sponsor/delete-account",
        data={"password": sponsor_password},
        follow_redirects=False,
    )
    if resp.status_code != 302:
        body = resp.get_data(as_text=True)[:5000]
        return _fail(f"Delete account expected 302, got {resp.status_code}. Body snippet:\n{body}")

    with app.app_context():
        acct = SponsorAccount.query.filter_by(email=sponsor_email).first()
        if acct is not None:
            return _fail("SponsorAccount still exists after deletion")
        sponsor = Sponsor.query.filter_by(email=sponsor_email).first()
        if sponsor is not None:
            return _fail("Sponsor profile still exists after deletion")

    print("OK: sponsor smoke test passed")
    return 0


if __name__ == "__main__":
    code = 1
    try:
        code = run()
    finally:
        # best-effort cleanup
        try:
            test_db_path = os.path.join(tempfile.gettempdir(), "bp_sponsor_smoke.db")
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
        except Exception:
            pass
    sys.exit(code)

