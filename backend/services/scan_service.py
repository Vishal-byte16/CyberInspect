from urllib.parse import urlparse
from backend.scanner.ssl_analyzer import analyze_ssl
from backend.scanner.headers_analyzer import analyze_headers
from backend.scanner.dns_analyzer import analyze_dns
from backend.scanner.http_analyzer import analyze_http
from backend.scanner.cookie_analyzer import analyze_cookies
from backend.scanner.domain_analyzer import analyze_domain
from backend.scanner.reputation_analyzer import analyze_reputation
from backend.scanner.tech_detector import detect_technology
from backend.services.scoring import calculate_score


def run_full_scan(full_url: str) -> dict:
    if not full_url.startswith(("http://", "https://")):
        full_url = "https://" + full_url
    host = urlparse(full_url).netloc.split(":")[0]

    data = {
        "ssl": analyze_ssl(host),
        "headers": analyze_headers(full_url),
        "dns": analyze_dns(host),
        "http": analyze_http(full_url),
        "cookies": analyze_cookies(full_url),
        "domain": analyze_domain(host),
        "reputation": analyze_reputation(host),
        "tech": detect_technology(full_url),
    }
    score, risk = calculate_score(data)
    data.update({"url": host, "full_url": full_url,
                 "score": score, "risk": risk})
    return data