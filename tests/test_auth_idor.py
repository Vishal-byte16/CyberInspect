"""
Regression test for item #2 from the test priorities: authentication /
authorization — specifically that one user cannot read or delete another
user's scans (IDOR). Uses an isolated sqlite file DB and a fully-mocked
scan result so no real network/whois calls happen.

Run: pytest tests/test_auth_idor.py -q
"""
import os, sys, tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Config must see valid-looking settings BEFORE any backend module is
# imported (utils/config.py validates eagerly at import time).
_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
os.environ["DATABASE_URL"] = f"sqlite:///{_db_file}"
os.environ["JWT_SECRET"] = "test-secret-" + "x" * 40
os.environ["ENVIRONMENT"] = "development"
os.environ["SEED_DEFAULT_USERS"] = "False"

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

FAKE_SCAN_RESULT = {
    "url": "example.com", "full_url": "https://example.com", "score": 90, "risk": "Excellent",
    "ssl": {"valid": True, "https": True, "chain_complete": True, "tls": ["TLSv1.3"]},
    "headers": {"headers": []},
    "dns": {"SPF": True, "DMARC": True, "DKIM": True, "A": "1.2.3.4"},
    "reputation": {"evaluated": False, "blacklisted": False, "phishing": False, "malware": False,
                   "summary": "Not Evaluated", "status": "not_evaluated"},
    "cookies": {"secure": True, "httpOnly": True, "sameSite": True, "count": 0},
    "http": {"status": 200, "server": "hidden", "response_time_rating": "Excellent"},
    "tech": {"server": "nginx", "cms": "None", "js": [], "cdn": "None", "proxy": "None"},
    "domain": {"ip": "1.2.3.4", "host": "Unknown"},
}


def _register_and_login(email):
    client.post("/api/auth/register", json={"name": "T", "email": email, "password": "password123"})
    r = client.post("/api/auth/login", data={"username": email, "password": "password123"})
    return r.json()["access_token"]


@patch("backend.api.scan_routes.run_full_scan", return_value=FAKE_SCAN_RESULT)
def test_user_cannot_read_or_delete_another_users_scan(_mock):
    token_a = _register_and_login("idor_a@test.com")
    token_b = _register_and_login("idor_b@test.com")

    r = client.post("/api/scan", json={"url": "example.com"},
                    headers={"Authorization": f"Bearer {token_a}"})
    assert r.status_code == 200
    scan_id = r.json()["id"]

    # Owner can read it.
    r = client.get(f"/api/scan/{scan_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert r.status_code == 200

    # A different logged-in user must NOT be able to read or delete it.
    r = client.get(f"/api/scan/{scan_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert r.status_code == 404

    r = client.delete(f"/api/scan/{scan_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert r.status_code == 404

    # Unauthenticated requests are rejected outright.
    r = client.get(f"/api/scan/{scan_id}")
    assert r.status_code in (401, 403)


def test_wrong_password_rejected():
    _register_and_login("idor_c@test.com")
    r = client.post("/api/auth/login", data={"username": "idor_c@test.com", "password": "wrong-password"})
    assert r.status_code == 401
