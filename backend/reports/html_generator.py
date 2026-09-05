import html


def _esc(v) -> str:
    return html.escape(str(v)) if v is not None else ""


def build_html(scan) -> str:
    d = scan.result or {}
    findings = list(getattr(scan, "findings", None) or [])

    full_url = _esc(scan.full_url)
    score = _esc(scan.score)
    risk = _esc(scan.risk_level)
    risk_color = {"Very Low": "#3DD68C", "Low": "#8FD694", "Medium": "#E3B341",
                  "High": "#E27A3C", "Critical": "#E5484D"}.get(scan.risk_level, "#8a9bc4")

    ssl = d.get("ssl", {})
    domain = d.get("domain", {})
    rep = d.get("reputation", {})
    ports = d.get("ports", {})

    # -----------------------------
    # Severity summary + positive controls (from real findings)
    # -----------------------------
    sev_order = ["critical", "high", "medium", "low", "info"]
    sev_counts = {s: 0 for s in sev_order}
    not_evaluated_count = 0
    positive_controls = []
    for f in findings:
        if f.status == "not_evaluated":
            not_evaluated_count += 1
            continue
        if f.status == "pass":
            positive_controls.append(f.title)
            continue
        sev_counts[f.severity if f.severity in sev_counts else "info"] += 1

    sev_row = "".join(f"<td>{sev_counts[s]}</td>" for s in sev_order) + f"<td>{not_evaluated_count}</td>"
    sev_header = "".join(f"<th>{s.capitalize()}</th>" for s in sev_order) + "<th>Not Evaluated</th>"

    controls_html = "".join(f"<li>&#10003; {_esc(t)}</li>" for t in positive_controls) or "<li>None recorded</li>"

    # -----------------------------
    # Security findings table
    # -----------------------------
    hdr_rows = "".join(
        f"<tr><td>{_esc(h['name'])}</td>"
        f"<td>{'Present' if h['present'] else 'Missing'}{' (weak)' if h.get('weak_reason') else ''}</td></tr>"
        for h in d.get("headers", {}).get("headers", [])
    )
    tls_versions = ssl.get("tls") or []
    tls_display = ", ".join(tls_versions) if tls_versions else "Unknown"
    tech = d.get("tech", {})
    cms = tech.get("cms")
    tech_display = cms if cms and cms != "None" else tech.get("server", "Unknown")
    blacklist_display = "Not Evaluated" if not rep.get("evaluated") else _esc(rep.get("blacklisted"))
    ports_display = "None exposed" if ports.get("all_closed", True) else f"{len(ports.get('open_ports', []))} exposed (see below)"

    findings_rows = "".join([
        f"<tr><td>HTTPS Enabled</td><td>{_esc(ssl.get('https'))}</td></tr>",
        f"<tr><td>Certificate Valid</td><td>{_esc(ssl.get('valid'))}</td></tr>",
        f"<tr><td>TLS Version</td><td>{_esc(tls_display)}</td></tr>",
        hdr_rows,
        f"<tr><td>SPF Record</td><td>{_esc(d.get('dns', {}).get('SPF'))}</td></tr>",
        f"<tr><td>DMARC Record</td><td>{_esc(d.get('dns', {}).get('DMARC'))}</td></tr>",
        f"<tr><td>DKIM</td><td>{_esc(d.get('dns', {}).get('DKIM'))}</td></tr>",
        f"<tr><td>Blacklist Status</td><td>{blacklist_display}</td></tr>",
        f"<tr><td>HTTP Status</td><td>{_esc(d.get('http', {}).get('status'))}</td></tr>",
        f"<tr><td>Server</td><td>{_esc(d.get('http', {}).get('server'))}</td></tr>",
        f"<tr><td>Technology</td><td>{_esc(tech_display)}</td></tr>",
        f"<tr><td>Open Ports</td><td>{_esc(ports_display)}</td></tr>",
    ])

    # -----------------------------
    # Open ports detail (only when something is exposed)
    # -----------------------------
    open_ports = ports.get("open_ports", [])
    ports_section = ""
    if open_ports:
        rows = "".join(
            f"<tr><td>{_esc(p['port'])}</td><td>{_esc(p['service'])}</td>"
            f"<td>{_esc(p['severity'].capitalize())}</td><td>{_esc(p['reason'])}</td></tr>"
            for p in open_ports
        )
        ports_section = f"""
    <h3>Exposed Ports</h3>
    <table><tr><th>Port</th><th>Service</th><th>Severity</th><th>Why it matters</th></tr>{rows}</table>"""

    # -----------------------------
    # Recommendations (from real findings, deduped)
    # -----------------------------
    seen = set()
    rec_items = []
    for f in findings:
        if f.status in ("fail", "warning") and f.recommendation and f.recommendation not in seen:
            seen.add(f.recommendation)
            tag = f" <span style='color:#8a9bc4'>[{_esc(f.owasp)}]</span>" if f.owasp else ""
            rec_items.append(f"<li>{_esc(f.recommendation)}{tag}</li>")
    recs_html = "".join(rec_items) or "<li>No major security improvements were detected.</li>"

    scan_date = _esc(getattr(scan, "created_at", ""))

    return f"""<html><head><meta charset='utf-8'><title>CyberInspect Report</title>
    <style>
      body{{font-family:Arial;padding:40px;color:#0d1f4c;max-width:900px;margin:0 auto}}
      h1{{color:#00a3b5}} h3{{color:#0d1f4c;margin-top:28px}}
      table{{border-collapse:collapse;width:100%;margin-top:8px}}
      td,th{{border:1px solid #e4ebf5;padding:8px;text-align:left}}
      th{{background:#0d1f4c;color:#fff}}
      .score-badge{{display:inline-block;padding:4px 12px;border-radius:6px;color:#fff;font-weight:bold;background:{risk_color}}}
      .meta-table td:first-child{{background:#eef4ff;font-weight:bold;width:200px}}
      ul{{padding-left:20px}} li{{margin-bottom:4px}}
      .note{{font-size:12px;color:#8a9bc4}}
    </style></head><body>
    <h1>&#128737;&#65039; CyberInspect Security Report</h1>

    <h3>Executive Summary</h3>
    <p>This report summarizes the automated security assessment of <b>{full_url}</b>.
    The website achieved a security score of <b>{score}/100</b>, resulting in an overall
    <span class="score-badge">{risk}</span> risk rating.</p>

    <table class="meta-table">
      <tr><td>Website</td><td>{full_url}</td></tr>
      <tr><td>Security Score</td><td>{score}/100</td></tr>
      <tr><td>Risk Level</td><td>{risk}</td></tr>
      <tr><td>Scan Date</td><td>{scan_date}</td></tr>
      <tr><td>Certificate Issuer</td><td>{_esc(ssl.get('issuer'))}</td></tr>
    </table>

    <h3>Severity Summary</h3>
    <table><tr>{sev_header}</tr><tr>{sev_row}</tr></table>
    {"<p class='note'>" + str(not_evaluated_count) + " check(s) could not be evaluated (e.g. no reputation provider configured) and are excluded from the score and severity counts above rather than being treated as passing.</p>" if not_evaluated_count else ""}

    <h3>Positive Security Controls</h3>
    <ul>{controls_html}</ul>

    <h3>Security Findings</h3>
    <table><tr><th>Check</th><th>Result</th></tr>{findings_rows}</table>
    {ports_section}

    <h3>Security Recommendations</h3>
    <ul>{recs_html}</ul>

    <h3>Website Information</h3>
    <table class="meta-table">
      <tr><td>IP Address</td><td>{_esc(domain.get('ip'))}</td></tr>
      <tr><td>Hosting</td><td>{_esc(domain.get('host', 'Unknown'))}</td></tr>
      <tr><td>Registrar</td><td>{_esc(domain.get('registrar'))}</td></tr>
      <tr><td>Domain Age</td><td>{_esc(domain.get('age'))}</td></tr>
    </table>

    <p class="note" style="margin-top:20px">
    This report is generated automatically using publicly observable technical indicators.
    It does not guarantee that a website is completely secure or vulnerable. Always perform
    manual testing and obtain authorization before conducting any security assessment.</p>
    <p class="note">Generated by CyberInspect &mdash; Website Security Assessment Platform</p>
    </body></html>"""