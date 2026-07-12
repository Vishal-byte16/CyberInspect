
def analyze_reputation(host: str) -> dict:
   
    return {
        "blacklisted": False,
        "phishing": False,
        "malware": False,
        "summary": "No threat feeds configured. Add API keys for live reputation data.",
        "evaluated": False,
    }