"""Convert raw scan data into normalized SecurityFinding rows."""
def extract_findings(data: dict) -> list[dict]:
    f = []
    ssl = data["ssl"]
    f.append(_mk("SSL/TLS", "HTTPS Available", ssl.get("https"),
                 "Served over HTTPS" if ssl.get("https") else "No HTTPS", "high"))
    f.append(_mk("SSL/TLS", "Certificate Valid", ssl.get("valid"),
                 f"Expires {ssl.get('expires')}", "high"))

    for h in data["headers"]["headers"]:
        f.append(_mk("Headers", h["name"], h["present"],
                     "Present" if h["present"] else "Missing", "medium"))

    dns = data["dns"]
    for key, sev in [("SPF", "medium"), ("DMARC", "medium"), ("DKIM", "low")]:
        f.append(_mk("DNS", f"{key} Record", dns.get(key),
                     "Configured" if dns.get(key) else "Missing", sev))

    ck = data["cookies"]
    for flag in ["secure", "httpOnly", "sameSite"]:
        f.append(_mk("Cookies", f"{flag} flag", ck.get(flag),
                     "Set" if ck.get(flag) else "Missing", "medium"))

    rep = data["reputation"]
    f.append(_mk("Reputation", "Blacklist", not rep.get("blacklisted"),
                 rep.get("summary"), "critical"))
    return f

def _mk(cat, title, ok, detail, sev):
    return {"category": cat, "title": title,
            "status": "pass" if ok else "fail",
            "detail": detail,
            "severity": "info" if ok else sev}