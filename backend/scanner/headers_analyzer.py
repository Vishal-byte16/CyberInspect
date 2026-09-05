from backend.utils.safe_http import safe_get

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
        r = safe_get(url, headers={
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"),
            "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9", "Connection": "close",
        })
        received = {k.lower() for k in r.headers.keys()}
        present = {
            h: h.lower() in received
            for h in SECURITY_HEADERS
        }

        def _quality(name, value):
            """Flag a present header that's configured weakly enough to
            give little real protection — real security value beyond
              just 'is it present'."""
            if value is None:
                return None
            if name == "Strict-Transport-Security":
                m = re_search_max_age(value)
                if m is not None and m < 15552000:  # < ~6 months
                    return f"max-age is only {m}s — recommend at least 15552000 (6 months)"
            if name == "Content-Security-Policy":
                low = value.lower()
                if "unsafe-inline" in low or "unsafe-eval" in low:
                    return "policy allows 'unsafe-inline'/'unsafe-eval', which weakens CSP's XSS protection"
            return None

        return {
    "headers": [
        {
            "name": h,
            "present": present[h],
            "value": r.headers.get(h),
            "weak_reason": _quality(h, r.headers.get(h)) if present[h] else None,
        }
        for h in SECURITY_HEADERS
    ],
    "raw": dict(r.headers),
}
    except Exception as e:
        return {
            "headers": [{"name": h, "present": False, "value": None, "weak_reason": None} for h in SECURITY_HEADERS],
            "error": str(e),
        }


def re_search_max_age(value: str):
    import re
    m = re.search(r"max-age=(\d+)", value or "", re.IGNORECASE)
    return int(m.group(1)) if m else None