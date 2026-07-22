import requests

BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/138.0.0.0 Safari/537.36")

def analyze_cookies(url: str) -> dict:
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": BROWSER_UA})
        cookies = r.raw.headers.getlist("Set-Cookie") if hasattr(r.raw.headers, "getlist") else \
                  [v for k, v in r.headers.items() if k.lower() == "set-cookie"]
        secure = any("secure" in c.lower() for c in cookies)
        http_only = any("httponly" in c.lower() for c in cookies)
        same_site = any("samesite" in c.lower() for c in cookies)
        return {"secure": secure, "httpOnly": http_only,
                "sameSite": same_site, "count": len(cookies)}
    except Exception as e:
        return {"secure": False, "httpOnly": False, "sameSite": False,
                "count": 0, "error": str(e)}