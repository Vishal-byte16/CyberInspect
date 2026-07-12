"""Scoring engine — matches the exact 100-point distribution & risk levels."""

WEIGHTS = {
    "ssl": 20,       # HTTPS & SSL/TLS
    "headers": 20,   # Security Headers
    "dns": 15,       # DNS Configuration
    "reputation": 20,# Website Reputation
    "cookies": 10,   # Cookie Security
    "http": 10,      # HTTP Configuration
    "tech": 5,       # Technology Detection
}

def calculate_score(data: dict) -> tuple[int, str]:
    ssl = data["ssl"]; headers = data["headers"]["headers"]
    dns = data["dns"]; rep = data["reputation"]
    cookies = data["cookies"]; http = data["http"]; tech = data["tech"]

    score = 0.0
    # SSL/TLS (20)
    if ssl.get("valid"): score += 14
    if ssl.get("https"): score += 3
    if ssl.get("chain_complete"): score += 3
    if any("deprecated" in str(t).lower() or "1.1" in str(t) or "1.0" in str(t)
           for t in ssl.get("tls", [])): score -= 4

    # Headers (20)
    present = sum(1 for h in headers if h["present"])
    score += present / max(1, len(headers)) * WEIGHTS["headers"]

    # DNS (15)
    score += (5 if dns.get("SPF") else 0) + (5 if dns.get("DMARC") else 0) \
           + (3 if dns.get("DKIM") else 0) + (2 if dns.get("A") != "—" else 0)

    # Reputation (20)
    if not (rep.get("blacklisted") or rep.get("phishing") or rep.get("malware")):
        score += WEIGHTS["reputation"]

    # Cookies (10)
    score += (4 if cookies.get("secure") else 0) + (3 if cookies.get("httpOnly") else 0) \
           + (3 if cookies.get("sameSite") else 0)

    # HTTP (10)
    if http.get("status") in (200, 301, 302): score += 5
    if http.get("server") == "Hidden (good)": score += 5
    else: score += 2

    # Tech (5)
    if tech.get("cdn") != "None": score += 3
    if tech.get("proxy") != "None": score += 2

    score = max(0, min(100, round(score)))
    return score, risk_level(score)


def risk_level(score: int) -> str:
    if score >= 90: return "Very Low"
    if score >= 75: return "Low"
    if score >= 50: return "Moderate"
    if score >= 25: return "High"
    return "Critical"