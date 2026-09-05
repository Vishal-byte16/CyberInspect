def analyze_reputation(host: str) -> dict:
    """No threat-intel provider is wired up. Explicitly NOT_EVALUATED —
    never fabricate a 'clean' result when nothing was actually checked."""
    return {
        "blacklisted": False,
        "phishing": False,
        "malware": False,
        "summary": "Not Evaluated — no threat feeds configured. Add API keys for live reputation data.",
        "evaluated": False,
        "status": "not_evaluated",
    }
