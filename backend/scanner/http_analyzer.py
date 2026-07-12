import requests

def analyze_http(url: str) -> dict:
    try:
        r = requests.get(url, timeout=8, allow_redirects=True,
                         headers={"User-Agent": "CyberInspect/1.0"})
        redirects = [f"{h.status_code} → {h.headers.get('Location','')}"
                     for h in r.history] or ["none"]
        server = r.headers.get("Server", "Hidden (good)")
        return {"status": r.status_code, "redirects": redirects,
                "server": server, "final_url": r.url}
    except Exception as e:
        return {"status": 0, "redirects": ["none"], "server": "Unknown", "error": str(e)}