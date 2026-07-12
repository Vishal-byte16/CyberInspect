import socket
try:
    import whois
except Exception:  # ImportError or linter unresolved import
    whois = None
from datetime import datetime

def analyze_domain(host: str) -> dict:
    res = {"age": "Unknown", "registrar": "Unknown",
           "expires": "Unknown", "ip": "Unknown", "host": "Unknown"}
    try:
        res["ip"] = socket.gethostbyname(host)
    except Exception:
        pass
    if whois is None:
        res["error"] = "whois library not installed"
        return res
    try:
        w = whois.whois(host)
        created = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
        expires = w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date
        if created:
            years = (datetime.now() - created).days // 365
            res["age"] = f"{years} years"
        if expires:
            res["expires"] = expires.strftime("%Y-%m-%d")
        res["registrar"] = w.registrar or "Unknown"
    except Exception as e:
        res["error"] = str(e)
    return res