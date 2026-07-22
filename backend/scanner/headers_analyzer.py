import requests

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
]


def analyze_headers(url: str) -> dict:
    try:
        r = requests.get(
            url,
            timeout=8,
            allow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/138.0.0.0 Safari/537.36"
                ),
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "close",
            },
        )
        received = {k.lower() for k in r.headers.keys()}
        present = {
            h: h.lower() in received
            for h in SECURITY_HEADERS
        }
        return {
    "headers": [
        {
            "name": h,
            "present": present[h],
            "value": r.headers.get(h)
        }
        for h in SECURITY_HEADERS
    ],
    "raw": dict(r.headers),
}
    except Exception as e:
        return {
            "headers": [{"name": h, "present": False} for h in SECURITY_HEADERS],
            "error": str(e),
        }