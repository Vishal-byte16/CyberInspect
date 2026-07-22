import requests
from backend.scanner.fingerprints import FINGERPRINTS
from bs4 import BeautifulSoup

def contains_any(text: str, patterns: list[str]) -> bool:
    """Return True if any pattern exists in text."""
    text = text.lower()

    for pattern in patterns:
        if pattern.lower() in text:
            return True

    return False


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

        headers = {k.lower(): v.lower() for k, v in r.headers.items()}

        html = r.text
        body = html.lower()

        soup = BeautifulSoup(html, "html.parser")

        script_urls = [
            (tag.get("src") or "").lower()
            for tag in soup.find_all("script")
        ]

        meta_values = [
            (
                (tag.get("name") or "")
                + " "
                + (tag.get("content") or "")
            ).lower()
            for tag in soup.find_all("meta")
        ]

        cookies = " ".join(r.cookies.keys()).lower()

        # -----------------------------
        # Generic Fingerprint Engine
        # -----------------------------

        for category, technologies in FINGERPRINTS.items():

            for tech_name, fingerprint in technologies.items():

                matched = False

                # --------------------
                # Header fingerprints
                # --------------------

                if "headers" in fingerprint:

                    for header_name, values in fingerprint["headers"].items():

                        if header_name.lower() not in headers:
                            continue

                        header_value = headers[header_name.lower()]

                        for value in values:

                            if value == "":
                                matched = True
                                break

                            if value.lower() in header_value:
                                matched = True
                                break

                        if matched:
                            break

                # --------------------
                # HTML fingerprints
                # --------------------

                if not matched and "html" in fingerprint:

                    if contains_any(body, fingerprint["html"]):
                        matched = True

                # --------------------
                # Cookie fingerprints
                # --------------------

                if not matched and "cookies" in fingerprint:

                    if contains_any(cookies, fingerprint["cookies"]):
                        matched = True

                # --------------------
                # Script fingerprints
                # --------------------

                if not matched and "scripts" in fingerprint:

                    for script in script_urls:

                        for pattern in fingerprint["scripts"]:

                            if pattern.lower() in script:
                                matched = True
                                break

                        if matched:
                            break

                # --------------------
                # Meta fingerprints
                # --------------------

                if not matched and "meta" in fingerprint:

                    for meta in meta_values:

                        for pattern in fingerprint["meta"]:

                            if pattern.lower() in meta:
                                matched = True
                                break

                        if matched:
                            break

                # --------------------
                # Store result
                # --------------------

                if matched:

                    if category == "server":
                        tech["server"] = tech_name

                    elif category == "cms":
                        tech["cms"] = tech_name

                    elif category in ("frontend", "backend"):

                        if tech_name not in tech["js"]:
                            tech["js"].append(tech_name)

                    elif category == "cdn":
                        tech["cdn"] = tech_name
                        tech["proxy"] = tech_name

        if not tech["js"]:
            tech["js"] = ["Vanilla JS"]

    except Exception as e:
        tech["error"] = str(e)

    return tech