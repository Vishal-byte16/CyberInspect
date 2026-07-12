import requests, re

def detect_technology(url: str) -> dict:
    tech = {"server": "Unknown", "cms": "None", "js": [],
            "cdn": "None", "proxy": "None"}
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "CyberInspect/1.0"})
        h = {k.lower(): v for k, v in r.headers.items()}
        body = r.text.lower()
        tech["server"] = h.get("server", "Unknown")
        if "cf-ray" in h or "cloudflare" in h.get("server", "").lower():
            tech["cdn"] = "Cloudflare"; tech["proxy"] = "Cloudflare"
        if "wp-content" in body or "wordpress" in body: tech["cms"] = "WordPress"
        elif "drupal" in body: tech["cms"] = "Drupal"
        elif "joomla" in body: tech["cms"] = "Joomla"
        for fw, pat in {"React": "react", "Vue": "vue", "Angular": "ng-",
                        "jQuery": "jquery", "Next.js": "_next"}.items():
            if pat in body: tech["js"].append(fw)
        if not tech["js"]: tech["js"] = ["Vanilla JS"]
    except Exception as e:
        tech["error"] = str(e)
    return tech