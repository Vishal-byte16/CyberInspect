import re
import socket

try:
    import whois
except Exception:  # ImportError or linter unresolved import
    whois = None

from datetime import datetime, timezone


def _apex(host: str) -> str:
    """WHOIS and domain-level records live on the registrable domain, not
    a 'www' (or other) subdomain — strip it so lookups actually hit."""
    if host.startswith("www."):
        return host[4:]
    return host


def _coerce_date(value):
    """python-whois sometimes returns strings instead of datetime objects
    depending on the registry — handle both instead of silently failing."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value

    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d-%b-%Y"):
        try:
            return datetime.strptime(str(value)[:19], fmt)
        except ValueError:
            continue
    return None


def analyze_domain(host: str) -> dict:
    res = {
        "age": "Unknown",
        "registrar": "Unknown",
        "created": "Unknown",
        "updated": "Unknown",
        "expires": "Unknown",
        "name_servers": [],
        "dnssec": "Unknown",
        "status": [],
        "ip": "Unknown",
        "host": "Unknown",
    }

    if not host:
        res["error"] = "No host provided"
        return res

    host = host.strip()

    ip = None
    try:
        ip = socket.gethostbyname(host)
        res["ip"] = ip
    except Exception:
        pass

    # Hosting provider: reverse-DNS the resolved IP (best-effort)
    if ip:
        try:
            ptr = socket.gethostbyaddr(ip)[0].lower()

            if "google" in ptr:
                res["host"] = "Google"
            elif "cloudflare" in ptr:
                res["host"] = "Cloudflare"
            elif "amazonaws" in ptr:
                res["host"] = "Amazon AWS"
            elif "azure" in ptr:
                res["host"] = "Microsoft Azure"
            else:
                res["host"] = ptr
        except Exception:
            pass

    if whois is None:
        res["error"] = "whois library not installed"
        return res

    apex = _apex(host)
    try:
        w = whois.whois(apex)

        created = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
        updated = w.updated_date[0] if isinstance(w.updated_date, list) else w.updated_date
        expires = w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date

        created = _coerce_date(created)
        updated = _coerce_date(updated)
        expires = _coerce_date(expires)

        if created:
            # Convert timezone-aware datetime to naive UTC
            if created.tzinfo is not None:
                created = created.astimezone(timezone.utc).replace(tzinfo=None)

            now = datetime.utcnow()
            days = (now - created).days
            res["age"] = f"{days // 365} years" if days >= 365 else f"{days} days"
            res["created"] = created.strftime("%Y-%m-%d")

        if updated:
            res["updated"] = updated.strftime("%Y-%m-%d")

        if expires:
            res["expires"] = expires.strftime("%Y-%m-%d")

        res["registrar"] = w.registrar or "Unknown"

        if getattr(w, "name_servers", None):
            if isinstance(w.name_servers, (list, set, tuple)):
                res["name_servers"] = sorted(list(w.name_servers))
            else:
                res["name_servers"] = [str(w.name_servers)]

        dnssec = getattr(w, "dnssec", None)
        if dnssec:
            res["dnssec"] = str(dnssec)

        status = getattr(w, "status", None)
        if status:
            if not isinstance(status, (list, tuple, set)):
                status = [status]

            cleaned = []
            for s in status:
                s = str(s)

                # Remove ICANN URLs
                s = re.sub(r"https?://\S+", "", s)

                # Remove any parentheses
                s = s.replace("(", "").replace(")", "")

                # Normalize whitespace
                s = " ".join(s.split())

                if s and s not in cleaned:
                    cleaned.append(s)

            res["status"] = cleaned

        if res["age"] == "Unknown" and res["registrar"] == "Unknown":
            res["error"] = "WHOIS returned no usable registration data for this domain"

    except Exception as e:
        res["error"] = str(e)

    return res
