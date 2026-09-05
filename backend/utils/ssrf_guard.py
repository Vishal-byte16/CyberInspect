"""SSRF protection: validate a URL/host is safe to fetch server-side."""
import ipaddress
import socket
from urllib.parse import urlparse

ALLOWED_SCHEMES = ("http", "https")
ALLOWED_PORTS = {80, 443}
BLOCKED_HOSTNAMES = {"localhost"}


class UnsafeScanTargetError(Exception):
    pass


def _is_public_ip(ip_str: str) -> bool:
    ip = ipaddress.ip_address(ip_str)
    return not (
        ip.is_private or ip.is_loopback or ip.is_link_local or
        ip.is_multicast or ip.is_reserved or ip.is_unspecified
    )


def assert_safe_target(raw_url: str) -> str:
    """Validate raw_url is safe to fetch. Returns hostname or raises UnsafeScanTargetError."""
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

    try:
        ipaddress.ip_address(host)
        if not _is_public_ip(host):
            raise UnsafeScanTargetError("This address is private/internal and cannot be scanned.")
        return host
    except ValueError:
        pass  # not a literal IP, resolve below

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
                "This host resolves to a private/internal IP and cannot be scanned."
            )
    return host
