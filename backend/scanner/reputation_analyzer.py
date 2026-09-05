"""
Reputation check via Google Safe Browsing API v4 (free tier: 10,000
lookups/day). If no API key is configured, this correctly reports
"Not Evaluated" rather than fabricating a "clean" result - see
utils/config.py GOOGLE_SAFE_BROWSING_API_KEY.
"""
import requests
from backend.utils.config import settings

SAFE_BROWSING_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
REQUEST_TIMEOUT = 5

THREAT_TYPES = ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"]


def analyze_reputation(url: str) -> dict:
    api_key = settings.GOOGLE_SAFE_BROWSING_API_KEY

    if not api_key:
        return {
            "blacklisted": False,
            "phishing": False,
            "malware": False,
            "summary": "Not Evaluated — no threat feeds configured. Add API keys for live reputation data.",
            "evaluated": False,
            "status": "not_evaluated",
        }

    payload = {
        "client": {"clientId": "cyberinspect", "clientVersion": "1.0.0"},
        "threatInfo": {
            "threatTypes": THREAT_TYPES,
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }

    try:
        resp = requests.post(
            SAFE_BROWSING_URL,
            params={"key": api_key},
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        matches = data.get("matches", [])

        if not matches:
            return {
                "blacklisted": False,
                "phishing": False,
                "malware": False,
                "summary": "Clean — not flagged by Google Safe Browsing.",
                "evaluated": True,
                "status": "pass",
            }

        threat_types_found = {m.get("threatType") for m in matches}
        phishing = "SOCIAL_ENGINEERING" in threat_types_found
        malware = "MALWARE" in threat_types_found or "POTENTIALLY_HARMFUL_APPLICATION" in threat_types_found

        return {
            "blacklisted": True,
            "phishing": phishing,
            "malware": malware,
            "summary": f"Flagged by Google Safe Browsing: {', '.join(sorted(threat_types_found))}.",
            "evaluated": True,
            "status": "fail",
        }

    except Exception as e:
        # A failed lookup is NOT the same as a clean result - report
        # honestly as not evaluated rather than assuming safety.
        return {
            "blacklisted": False,
            "phishing": False,
            "malware": False,
            "summary": f"Not Evaluated — reputation check failed ({e}).",
            "evaluated": False,
            "status": "not_evaluated",
        }