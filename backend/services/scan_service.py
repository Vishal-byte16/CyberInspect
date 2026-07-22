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
from backend.utils.ssrf_guard import assert_safe_target


def run_full_scan(full_url: str) -> dict:
    if not full_url.startswith(("http://", "https://")):
        full_url = "https://" + full_url

    # SSRF guard: refuses to proceed if this host resolves to a private/
    # internal/loopback address (localhost, internal network, cloud
    # metadata endpoint, etc). Raises UnsafeScanTargetError otherwise,
    # which the API route turns into a 400.
    host = assert_safe_target(full_url)

    ssl_result = analyze_ssl(host)
    # If HTTPS genuinely isn't available, re-run the live checks against
    # plain HTTP instead of letting them fail pointlessly against a port
    # that never answered.
    request_url = full_url
    if not ssl_result["https"] and full_url.startswith("https://"):
        request_url = "http://" + host

    headers_result = analyze_headers(request_url)
    http_result = analyze_http(request_url)
    tech_result = detect_technology(request_url)

    data = {
        "ssl": ssl_result,
        "headers": headers_result,
        "dns": analyze_dns(host),
        "http": http_result,
        "cookies": analyze_cookies(request_url),
        "domain": analyze_domain(host),
        "reputation": analyze_reputation(host),
        "tech": tech_result,
    }

    # If the live HTTP layer never got a response on either scheme, this
    # wasn't a real security assessment - say so explicitly rather than
    # presenting defaulted/empty fields as confirmed findings.
    if http_result.get("status") == 0:
        data["connection_error"] = (
            "Could not connect to this site over HTTPS or HTTP "
            f"({http_result.get('error', 'connection failed')}). "
            "The results below reflect DNS/reputation checks only - "
            "header, SSL, and technology findings could not be verified."
        )

    score, risk = calculate_score(data)
    data.update({"url": host, "full_url": request_url,
                 "score": score, "risk": risk})

    # A connection failure isn't a confirmed security finding - don't let it
    # masquerade as a scored, Critical-risk assessment.
    if "connection_error" in data:
        data["risk"] = "Incomplete"

    return data