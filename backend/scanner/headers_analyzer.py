import requests

SECURITY_HEADERS = [
    "Content-Security-Policy", "Strict-Transport-Security", "X-Frame-Options",
    "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy",
]

def analyze_headers(url: str) -> dict:
    try:
        r = requests.get(url, timeout=8, allow_redirects=True,
                         headers={"User-Agent": "CyberInspect/1.0"})
        present = {h: (h in r.headers) for h in SECURITY_HEADERS}
        return {"headers": [{"name": h, "present": present[h]} for h in SECURITY_HEADERS],
                "raw": dict(r.headers)}
    except Exception as e:
        return {"headers": [{"name": h, "present": False} for h in SECURITY_HEADERS],
                "error": str(e)}