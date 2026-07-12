import dns.resolver

def _q(host, rtype):
    try:
        return [r.to_text() for r in dns.resolver.resolve(host, rtype, lifetime=5)]
    except Exception:
        return []

def analyze_dns(host: str) -> dict:
    a = _q(host, "A"); aaaa = _q(host, "AAAA")
    mx = _q(host, "MX"); ns = _q(host, "NS")
    txt = _q(host, "TXT"); cname = _q(host, "CNAME")
    spf = any("v=spf1" in t.lower() for t in txt)
    dmarc = bool(_q(f"_dmarc.{host}", "TXT"))
    dkim = bool(_q(f"default._domainkey.{host}", "TXT"))
    return {
        "A": a[0] if a else "—", "AAAA": aaaa[0] if aaaa else "—",
        "MX": mx[0] if mx else "—", "NS": ns[0] if ns else "—",
        "TXT": txt[0] if txt else "—", "CNAME": cname[0] if cname else "—",
        "SPF": spf, "DMARC": dmarc, "DKIM": dkim,
    }