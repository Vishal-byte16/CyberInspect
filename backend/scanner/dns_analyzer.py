import dns.resolver

def _q(host, rtype):
    try:
        return [r.to_text() for r in dns.resolver.resolve(host, rtype, lifetime=5)]
    except Exception:
        return []

def _apex(host: str) -> str:
    """MX/NS/TXT/SPF/DMARC/DKIM records live on the registrable domain,
    not a 'www' subdomain — checking the literal typed host here would
    near-always come back empty even when the domain is properly configured."""
    if host.startswith("www."):
        return host[4:]
    return host

def analyze_dns(host: str) -> dict:
    apex = _apex(host)
    # A/AAAA/CNAME describe the exact host being scanned — keep those literal.
    a = _q(host, "A"); aaaa = _q(host, "AAAA"); cname = _q(host, "CNAME")
    # Everything else is domain-wide, not subdomain-specific — use the apex.
    mx = _q(apex, "MX"); ns = _q(apex, "NS"); txt = _q(apex, "TXT")
    spf = any("v=spf1" in t.lower() for t in txt)
    dmarc = bool(_q(f"_dmarc.{apex}", "TXT"))
    dkim = bool(_q(f"default._domainkey.{apex}", "TXT"))
    return {
        "A": a[0] if a else "—", "AAAA": aaaa[0] if aaaa else "—",
        "MX": mx[0] if mx else "—", "NS": ns[0] if ns else "—",
        "TXT": txt[0] if txt else "—", "CNAME": cname[0] if cname else "—",
        "SPF": spf, "DMARC": dmarc, "DKIM": dkim,
    }
