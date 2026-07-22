"""
SSRF (Server-Side Request Forgery) protection for the website scanner.

CyberInspect accepts an arbitrary URL from the user and makes outbound HTTP
requests to it from the server. Without this guard, someone could submit a
URL pointing at localhost, an internal service, or a cloud metadata endpoint
(e.g. 169.254.169.254) and use the scanner to probe or exfiltrate data from
your own infrastructure.

Call `assert_safe_target(url)` before any scanner module touches the URL.

Note: this closes the common case (someone typing an internal IP/hostname
directly). It does not fully defend against DNS-rebinding attacks, where a
domain resolves to a public IP at check-time and a private IP at
request-time. Fully closing that gap requires pinning the resolved IP for
the actual HTTP request (e.g. a custom requests Transport/HTTPAdapter), which
is a larger change than this patch makes. For now this guard should be
treated as a strong baseline, not a complete SSRF solution.
"""
import ipaddress
import socket
from urllib.parse import urlparse

ALLOWED_SCHEMES = ("http", "https")
ALLOWED_PORTS = {80, 443}
BLOCKED_HOSTNAMES = {"localhost"}


class UnsafeScanTargetError(Exception):
    """Raised when a requested scan target is not safe to reach."""


def _is_public_ip(ip_str: str) -> bool:
    ip = ipaddress.ip_address(ip_str)
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def assert_safe_target(raw_url: str) -> str:
    """
    Validate that `raw_url` is safe for the server to fetch.

    Returns the validated hostname on success.
    Raises UnsafeScanTargetError with a user-facing message otherwise.
    """
    url = raw_url.strip()
    if "://" not in url:
        url = "https://" + url

    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise UnsafeScanTargetError("Only http:// and https:// URLs can be scanned.")

    host = (parsed.hostname or "").strip().lower()
    if not host:
        raise UnsafeScanTargetError("Could not determine a hostname to scan.")

    if host in BLOCKED_HOSTNAMES or host.endswith(".local"):
        raise UnsafeScanTargetError("Scanning local or internal hosts is not allowed.")

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if port not in ALLOWED_PORTS:
        raise UnsafeScanTargetError(f"Scanning on port {port} is not allowed.")

    # If the host was typed as a raw IP, validate it directly.
    try:
        ipaddress.ip_address(host)
        if not _is_public_ip(host):
            raise UnsafeScanTargetError(
                "This address is private or internal and cannot be scanned."
            )
        return host
    except ValueError:
        pass  # Not a literal IP — resolve it below.

    try:
        addrinfo = socket.getaddrinfo(host, port)
    except socket.gaierror:
        raise UnsafeScanTargetError(f"Could not resolve host: {host}")

    resolved_ips = {info[4][0] for info in addrinfo}
    if not resolved_ips:
        raise UnsafeScanTargetError(f"Could not resolve host: {host}")

    for ip_str in resolved_ips:
        if not _is_public_ip(ip_str):
            raise UnsafeScanTargetError(
                "This host resolves to a private or internal IP address "
                "and cannot be scanned."
            )

    return host