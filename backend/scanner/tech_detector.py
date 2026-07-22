import requests, re

def detect_technology(url: str) -> dict:
    tech = {
        "server": "Unknown",
        "cms": "None",
        "js": [],
        "cdn": "None",
        "proxy": "None",
    }
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
                )
            },
        )
        h = {k.lower(): v for k, v in r.headers.items()}
        body = r.text.lower()
        server = h.get("server", "")
        if not server or server.lower() == "server":
            tech["server"] = "Unknown"
        else:
            tech["server"] = server

        server_l = server.lower() if server else ""
        # CDN / proxy detection
        if "cf-ray" in h or "cloudflare" in server_l:
            tech["cdn"] = "Cloudflare"
            tech["proxy"] = "Cloudflare"
        elif "akamai" in body or "akamai" in server_l:
            tech["cdn"] = "Akamai"
        elif "cloudfront" in server_l:
            tech["cdn"] = "Amazon CloudFront"
        elif "fastly" in server_l:
            tech["cdn"] = "Fastly"

        # CMS detection
        if "wp-content" in body or "wordpress" in body:
            tech["cms"] = "WordPress"
        elif "drupal" in body:
            tech["cms"] = "Drupal"
        elif "joomla" in body:
            tech["cms"] = "Joomla"
        # React
        if "__REACT_DEVTOOLS_GLOBAL_HOOK__" in r.text or "data-reactroot" in body:
            tech["js"].append("React")

        # Vue
        if "__VUE__" in r.text or "data-v-" in body:
            tech["js"].append("Vue")

        # Angular
        if "ng-version" in body or "ng-app" in body:
            tech["js"].append("Angular")

        # Next.js
        if "/_next/" in body or "__NEXT_DATA__" in r.text:
            tech["js"].append("Next.js")

        # jQuery
        if "jquery" in body and ("jquery.min.js" in body or "window.jquery" in body):
            tech["js"].append("jQuery")
        if not tech["js"]: tech["js"] = ["Vanilla JS"]
    except Exception as e:
        tech["error"] = str(e)
    return tech