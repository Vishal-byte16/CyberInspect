"""Centralized SSRF-safe HTTP fetch: manual redirect validation, timeout, size cap."""
import requests
from urllib.parse import urljoin
from backend.utils.ssrf_guard import assert_safe_target, UnsafeScanTargetError

CONNECT_TIMEOUT = 5
READ_TIMEOUT = 8
MAX_REDIRECTS = 5
MAX_BYTES = 5 * 1024 * 1024  # 5 MB cap on any single scanned response


def safe_get(url: str, headers: dict | None = None) -> requests.Response:
    """GET url with each redirect hop re-validated against SSRF rules, a
    connect+read timeout, and a hard cap on response size."""
    assert_safe_target(url)
    current = url
    redirect_chain = []
    for _ in range(MAX_REDIRECTS + 1):
        resp = requests.get(current, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                            headers=headers, allow_redirects=False, stream=True)
        if resp.status_code in (301, 302, 303, 307, 308):
            location = resp.headers.get("Location")
            redirect_chain.append((resp.status_code, location or ""))
            resp.close()
            if not location:
                resp.redirect_chain = redirect_chain
                return resp
            next_url = urljoin(current, location)
            assert_safe_target(next_url)  # validate BEFORE following
            current = next_url
            continue

        content = b""
        for chunk in resp.iter_content(8192):
            content += chunk
            if len(content) > MAX_BYTES:
                resp.close()
                raise ValueError("Response exceeded the maximum allowed size (5MB)")
        resp._content = content
        resp.redirect_chain = redirect_chain
        return resp

    raise UnsafeScanTargetError("Too many redirects.")
