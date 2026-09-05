"""High-value regression tests. Run: pytest tests/test_security.py -q
No DB/app boot required — pure-logic modules only.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from backend.utils.ssrf_guard import assert_safe_target, UnsafeScanTargetError
from backend.services.scoring import calculate_score
from backend.scanner.reputation_analyzer import analyze_reputation


# ---------- SSRF protection ----------
@pytest.mark.parametrize("url", [
    "http://127.0.0.1", "http://localhost:8000", "http://169.254.169.254/latest/meta-data/",
    "http://192.168.1.1", "http://10.0.0.5", "http://0.0.0.0", "ftp://example.com",
])
def test_ssrf_blocks_unsafe_targets(url):
    with pytest.raises(UnsafeScanTargetError):
        assert_safe_target(url)

@pytest.mark.parametrize("url", ["https://8.8.8.8", "example.com", "https://openai.com"])
def test_ssrf_allows_public_targets(url):
    assert assert_safe_target(url)


# ---------- Reputation: NOT_EVALUATED must never look like "clean" ----------
def test_reputation_reports_not_evaluated():
    rep = analyze_reputation("example.com")
    assert rep["evaluated"] is False
    assert rep["status"] == "not_evaluated"
    assert "not evaluated" in rep["summary"].lower()


# ---------- Scoring: unevaluated/errored categories must not earn full marks ----------
def _base_data(**overrides):
    data = {
        "ssl": {"valid": True, "https": True, "chain_complete": True, "tls": ["TLSv1.3"]},
        "headers": {"headers": [{"name": "X", "present": True}] * 4},
        "dns": {"SPF": True, "DMARC": True, "DKIM": True, "A": "1.2.3.4"},
        "reputation": {"evaluated": False, "blacklisted": False, "phishing": False, "malware": False},
        "cookies": {"secure": True, "httpOnly": True, "sameSite": True},
        "http": {"status": 200, "response_time_rating": "Excellent", "server": "hidden"},
        "tech": {"server": "nginx", "cms": "None"},
    }
    data.update(overrides)
    return data

def test_unevaluated_reputation_scores_zero_not_full():
    score_unevaluated, _ = calculate_score(_base_data())
    score_evaluated_clean, _ = calculate_score(
        _base_data(reputation={"evaluated": True, "blacklisted": False, "phishing": False, "malware": False})
    )
    # Not-evaluated must score strictly lower than a confirmed-clean result -
    # i.e. NOT_EVALUATED is never treated as PASS.
    assert score_unevaluated < score_evaluated_clean
    assert score_evaluated_clean - score_unevaluated == 20  # full reputation weight withheld

def test_cookie_scan_error_scores_zero_for_cookies():
    ok_score, _ = calculate_score(_base_data())
    err_score, _ = calculate_score(_base_data(cookies={"error": "timeout"}))
    assert err_score < ok_score

def test_tech_detection_error_scores_zero_for_tech():
    ok_score, _ = calculate_score(_base_data())
    err_score, _ = calculate_score(_base_data(tech={"error": "timeout"}))
    assert err_score == ok_score - 5

def test_score_never_exceeds_100_when_everything_passes():
    score, risk = calculate_score(_base_data(
        reputation={"evaluated": True, "blacklisted": False, "phishing": False, "malware": False}
    ))
    assert 0 <= score <= 100
    assert risk in ("Excellent", "Low", "Medium", "High", "Critical")
