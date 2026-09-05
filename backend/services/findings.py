"""Convert raw scan data into normalized SecurityFinding rows.

Status is one of: pass | fail | warning | not_evaluated | error — a
NOT_EVALUATED check is never reported as a pass/"clean" result.
"""

def extract_findings(data: dict) -> list[dict]:
    f = []
    ssl = data["ssl"]
    f.append(_mk("SSL/TLS", "HTTPS Available", "pass" if ssl.get("https") else "fail",
                 "Served over HTTPS" if ssl.get("https") else "Site is not served over HTTPS",
                 "high", impact="Traffic without HTTPS can be intercepted or tampered with in transit.",
                 recommendation="Serve all traffic over HTTPS and redirect HTTP to HTTPS.",
                 owasp="A02:2021-Cryptographic Failures", cwe="CWE-319"))
    f.append(_mk("SSL/TLS", "Certificate Valid", "pass" if ssl.get("valid") else "fail",
                 f"Expires {ssl.get('expires')}", "high",
                 impact="An invalid/expired certificate breaks trust and browser warnings may train users to click through security alerts.",
                 recommendation="Renew or reissue the TLS certificate before expiry.",
                 owasp="A02:2021-Cryptographic Failures", cwe="CWE-295"))

    for h in data["headers"]["headers"]:
        weak = h.get("weak_reason")
        status = "pass" if h["present"] and not weak else ("warning" if h["present"] else "warning")
        detail = weak if weak else ("Present" if h["present"] else "Missing")
        f.append(_mk("Headers", h["name"], status, detail, "medium",
                     confidence="high",
                     impact="Missing or weakly-configured security headers widen the attack surface for clickjacking, MIME-sniffing, or injection-based attacks depending on the header.",
                     recommendation=(f"Strengthen the {h['name']} header configuration." if weak
                                     else f"Add the {h['name']} header with an appropriate policy."),
                     owasp="A05:2021-Security Misconfiguration", cwe="CWE-693"))

    dns = data["dns"]
    dns_meta = {
        "SPF": ("medium", "CWE-290", "Add an SPF record authorizing your legitimate mail servers."),
        "DMARC": ("medium", "CWE-290", "Add a DMARC record to define handling of unauthenticated mail."),
        "DKIM": ("low", "CWE-290", "Enable DKIM signing on outbound mail."),
    }
    for key, (sev, cwe, rec) in dns_meta.items():
        f.append(_mk("DNS", f"{key} Record", "pass" if dns.get(key) else "warning",
                     "Configured" if dns.get(key) else "Missing", sev,
                     impact="Missing email-authentication records make the domain easier to spoof in phishing campaigns.",
                     recommendation=rec, owasp="A07:2021-Identification and Authentication Failures", cwe=cwe))

    ck = data["cookies"]
    if ck.get("error"):
        f.append(_mk("Cookies", "Cookie Security", "error", f"Could not evaluate: {ck['error']}", "info",
                     confidence="low", impact="Cookie security attributes could not be checked."))
    else:
        for flag, label in [("secure", "Secure flag"), ("httpOnly", "HttpOnly flag"), ("sameSite", "SameSite flag")]:
            f.append(_mk("Cookies", label, "pass" if ck.get(flag) else "warning",
                         "Set" if ck.get(flag) else "Missing", "medium",
                         impact="Missing cookie flags increase exposure to session theft (XSS) or CSRF depending on the flag.",
                         recommendation=f"Set the {label} attribute on session cookies.",
                         owasp="A05:2021-Security Misconfiguration", cwe="CWE-1004"))

    rep = data["reputation"]
    if not rep.get("evaluated"):
        f.append(_mk("Reputation", "Blacklist / Threat Intel", "not_evaluated",
                     rep.get("summary", "Not Evaluated"), "info", confidence="low",
                     impact="No conclusion can be drawn — this is not confirmation the site is clean.",
                     recommendation="Configure a threat-intelligence/blacklist provider for this check to run."))
    else:
        is_clean = not (rep.get("blacklisted") or rep.get("phishing") or rep.get("malware"))
        f.append(_mk("Reputation", "Blacklist / Threat Intel", "pass" if is_clean else "fail",
                     rep.get("summary"), "critical",
                     impact="A blacklisted/flagged domain indicates active abuse (phishing/malware) associated with the site.",
                     recommendation="Investigate and request delisting from the relevant blacklist providers." if not is_clean else None))
    ports = data.get("ports", {})
    if ports.get("all_closed"):
        f.append(_mk("Network", "Open Ports", "pass",
                     f"None of {ports.get('checked', 0)} commonly-risky ports (databases, remote admin, "
                     "legacy protocols) are exposed.", "info",
                     evidence=f"Checked {ports.get('checked', 0)} ports; none open."))
    else:
        for p in ports.get("open_ports", []):
            f.append(_mk("Network", f"Port {p['port']} ({p['service']}) Exposed", "fail",
                         p["reason"], p["severity"], confidence="high",
                         impact=f"{p['service']} is reachable from the internet on port {p['port']}. "
                                f"{p['reason']}",
                         recommendation=f"Restrict port {p['port']} to trusted IPs via firewall/security group, "
                                        "or bind the service to a private network interface only.",
                         evidence=f"TCP connect to port {p['port']} succeeded.",
                         owasp="A05:2021-Security Misconfiguration", cwe="CWE-16"))
    return f


def _mk(cat, title, status, detail, severity, confidence="high",
        impact=None, recommendation=None, evidence=None, owasp=None, cwe=None):
    return {
        "category": cat, "title": title, "status": status, "detail": detail,
        "severity": "info" if status in ("pass", "not_evaluated") else severity,
        "confidence": confidence, "impact": impact, "recommendation": recommendation,
        "evidence": evidence or detail, "owasp": owasp, "cwe": cwe,
    }
