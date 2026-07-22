import time
import requests

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/138.0.0.0 Safari/537.36"
)


STATUS_INFO = {
    200: ("200 OK", "The website responded successfully."),
    201: ("201 Created", "The request succeeded and created a new resource."),
    204: ("204 No Content", "The server processed the request but returned no content."),
    301: ("301 Moved Permanently", "The website permanently redirects visitors to another URL."),
    302: ("302 Found", "The website temporarily redirects visitors."),
    304: ("304 Not Modified", "The browser can use its cached copy of this page."),
    400: ("400 Bad Request", "The server could not understand the request."),
    401: ("401 Unauthorized", "Authentication is required."),
    403: ("403 Forbidden", "The server refused access to this page."),
    404: ("404 Not Found", "The requested page does not exist."),
    412: ("412 Precondition Failed",
          "The server rejected this request. Some websites intentionally do this for automated scanners."),
    429: ("429 Too Many Requests",
          "The website is rate-limiting requests."),
    500: ("500 Internal Server Error",
          "The website encountered an internal server error."),
    502: ("502 Bad Gateway",
          "The server received an invalid response from another server."),
    503: ("503 Service Unavailable",
          "The website is temporarily unavailable."),
}

def get_response_rating(ms):
    if ms <= 300:
        return "Excellent"
    elif ms <= 800:
        return "Good"
    elif ms <= 1500:
        return "Moderate"
    elif ms <= 3000:
        return "Slow"
    else:
        return "Very Slow"
    
def analyze_http(url: str) -> dict:
    try:
        start = time.perf_counter()

        r = requests.get(
            url,
            timeout=8,
            allow_redirects=True,
            headers={"User-Agent": BROWSER_UA},
        )

        elapsed = round((time.perf_counter() - start) * 1000)

        redirects = []

        for h in r.history:
            redirects.append(f"{h.status_code} → {h.headers.get('Location','')}")

        if not redirects:
            redirects = ["No redirects"]

        server = r.headers.get("Server")

        if not server or server.lower() in ("server", ""):
            server = "Hidden"

        title, explanation = STATUS_INFO.get(
            r.status_code,
            (str(r.status_code), "No additional information available.")
        )

        return {
            "status": r.status_code,
            "status_title": title,
            "status_explanation": explanation,
            "response_time": elapsed,
            "response_time_rating": get_response_rating(elapsed),
            "redirects": redirects,
            "server": server,
            "final_url": r.url,
        }

    except Exception as e:
        return {
            "status": 0,
            "status_title": "Unreachable",
            "status_explanation": "The website could not be reached.",
          "response_time": None,
          "response_time_rating": "Unknown",
            "redirects": ["No redirects"],
            "server": "Unknown",
            "error": str(e),
        }