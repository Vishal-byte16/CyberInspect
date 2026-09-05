"""Scoring engine — 100-point distribution. Categories that were not
actually evaluated contribute 0, never full marks."""

WEIGHTS = {
    "ssl": 20, "headers": 20, "dns": 15, "reputation": 20,
    "cookies": 10, "http": 10, "ports": 5,
}

def calculate_score(data: dict) -> tuple[int, str]:
    ssl = data["ssl"]; headers = data["headers"]["headers"]
    dns = data["dns"]; rep = data["reputation"]
    cookies = data["cookies"]; http = data["http"]

    score = 0.0
    # SSL/TLS (20)
    if ssl.get("valid"): score += 14
    if ssl.get("https"): score += 3
    if ssl.get("chain_complete"): score += 3
    if any("deprecated" in str(t).lower() or "1.1" in str(t) or "1.0" in str(t)
           for t in ssl.get("tls", [])): score -= 4

    # Headers (20) — a present-but-weak header (e.g. short HSTS max-age,
    # CSP with unsafe-inline) earns half credit, not a full pass.
    header_points = sum(1.0 if (h["present"] and not h.get("weak_reason"))
                        else 0.5 if h["present"] else 0.0
                        for h in headers)
    score += header_points / max(1, len(headers)) * WEIGHTS["headers"]

    # DNS (15)
    score += (5 if dns.get("SPF") else 0) + (5 if dns.get("DMARC") else 0) \
           + (3 if dns.get("DKIM") else 0) + (2 if dns.get("A") != "—" else 0)

    # Reputation (20) — NOT_EVALUATED must never score as PASS. If no
    # reputation provider is configured, this category contributes 0
    # points and is reported separately as "Not Evaluated", not "Clean".
    if rep.get("evaluated"):
        if not (rep.get("blacklisted") or rep.get("phishing") or rep.get("malware")):
            score += WEIGHTS["reputation"]
    # else: not evaluated -> 0 points, no fabricated "clean" credit

    # Cookies (10) — only earn points for attributes actually confirmed
    # present; a scan error or absence of cookies earns nothing (not a
    # free baseline).
    if not cookies.get("error"):
        if cookies.get("secure"): score += 4
        if cookies.get("httpOnly"): score += 3
        if cookies.get("sameSite"): score += 3

    # HTTP (10)
    if http.get("status") in (200, 301, 302):
        score += 4
    rating = http.get("response_time_rating", "")
    if rating == "Excellent": score += 4
    elif rating == "Good": score += 3
    elif rating == "Moderate": score += 2
    elif rating == "Slow": score += 1
    server = str(http.get("server", "")).lower()
    if server in ("hidden", "hidden (good)", "", "unknown"):
        score += 2

    # Open Ports (5) — full marks if none of the checked risky ports are
    # exposed; each open port deducts based on severity, floored at 0.
    ports = data.get("ports", {})
    port_deduct = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    deduction = sum(port_deduct.get(p.get("severity"), 2) for p in ports.get("open_ports", []))
    score += max(0, WEIGHTS["ports"] - deduction)

    score = max(0, min(100, round(score)))
    return score, risk_level(score)


def risk_level(score: int) -> str:
    if score >= 90: return "Excellent"
    if score >= 75: return "Low"
    if score >= 60: return "Medium"
    if score >= 40: return "High"
    return "Critical"
