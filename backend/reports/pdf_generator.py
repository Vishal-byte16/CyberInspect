from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, grey, white
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from xml.sax.saxutils import escape as _xml_escape

import os
def build_pdf(scan) -> bytes:

    buf = BytesIO()
    # scan.full_url includes the raw path/query the user typed and can
    # contain characters ReportLab's Paragraph markup would interpret
    # (<, >, &) — escape before embedding in any Paragraph.
    safe_full_url = _xml_escape(str(scan.full_url))

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        textColor=HexColor("#0d1f4c"),
        fontSize=24,
        spaceAfter=12
    )

    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        textColor=HexColor("#0d1f4c"),
        spaceAfter=5
    )

    normal = styles["BodyText"]

    d = getattr(scan, "result", {}) or {}
    findings = list(getattr(scan, "findings", None) or [])

    # -----------------------------
    # Severity Summary (from real findings, not fabricated)
    # -----------------------------
    sev_order = ["critical", "high", "medium", "low", "info"]
    sev_counts = {s: 0 for s in sev_order}
    not_evaluated_count = 0
    positive_controls = []
    for fnd in findings:
        if fnd.status == "not_evaluated":
            not_evaluated_count += 1
            continue
        if fnd.status == "pass":
            positive_controls.append(fnd.title)
            continue
        sev_counts[fnd.severity if fnd.severity in sev_counts else "info"] += 1

    # -----------------------------
    # Security Headers
    # -----------------------------
    headers_list = d.get("headers", {}).get("headers", [])

    headers_present = sum(1 for h in headers_list if h.get("present"))

    total_headers = len(headers_list)

    # -----------------------------
    # Recommendations (from real findings; falls back to the basic checks
    # below only if findings weren't persisted for this scan)
    # -----------------------------
    recommendations = []
    seen = set()
    for fnd in findings:
        if fnd.status in ("fail", "warning") and fnd.recommendation and fnd.recommendation not in seen:
            seen.add(fnd.recommendation)
            tag = f" [{fnd.owasp}]" if fnd.owasp else ""
            recommendations.append(f"\u2022 {fnd.recommendation}{tag}")

    if not recommendations and not findings:
        if not d.get("ssl", {}).get("https"):
            recommendations.append(
                "• Enable HTTPS to encrypt traffic."
            )

        if not d.get("ssl", {}).get("valid"):
            recommendations.append(
                "• Install a valid SSL certificate."
            )

        for header in headers_list:
            if not header.get("present"):
                name = header.get("name", "Unknown Header")
                recommendations.append(f"• Add {name} security header.")

        if not d.get("dns", {}).get("SPF"):
            recommendations.append(
                "• Configure an SPF record."
            )

        if not d.get("dns", {}).get("DMARC"):
            recommendations.append(
                "• Configure a DMARC policy."
            )

        if not d.get("dns", {}).get("DKIM"):
            recommendations.append(
                "• Enable DKIM signing."
            )

    if not recommendations:
        recommendations.append(
            "Excellent! No major security improvements were detected."
        )

    # -----------------------------
    # Document
    # -----------------------------
    story = []

    logo_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "frontend",
        "assets",
        "logo.jpeg"
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path)
        logo.drawWidth = 28 * mm
        logo.drawHeight = 28 * mm
        story.append(logo)
        story.append(Spacer(1, 6))
        
        story.append(
            Paragraph("CyberInspect Security Report", title)
        )

        story.append(
            Paragraph(
                "<b>Executive Summary</b>",
                heading
            )
        )

        story.append(
            Paragraph(
                f"""
                This report summarizes the automated security assessment of
                <b>{safe_full_url}</b>. The website achieved a security score
                of <b>{scan.score}/100</b>, resulting in an overall
                <b>{scan.risk_level}</b> risk rating.
                """,
                normal,
            )
        )

    story.append(Spacer(1, 10))

    # -----------------------------
    # Scan Information
    # -----------------------------

    info = Table([
    ["Website", scan.full_url],
    ["Security Score", f"{scan.score}/100"],
    ["Risk Level", scan.risk_level],
    ["Scan Date", str(scan.created_at)],
    ["Certificate Issuer", str(d.get("ssl", {}).get("issuer"))],
    ], colWidths=[55 * mm, 115 * mm])

    info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), white),
        ("GRID", (0, 0), (-1, -1), 0.4, grey),
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#eef4ff")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(info)

    story.append(Spacer(1, 12))

    # -----------------------------
    # Severity Summary
    # -----------------------------
    story.append(Paragraph("Severity Summary", heading))
    sev_row = Table([
        ["Critical", "High", "Medium", "Low", "Info", "Not Evaluated"],
        [str(sev_counts["critical"]), str(sev_counts["high"]), str(sev_counts["medium"]),
         str(sev_counts["low"]), str(sev_counts["info"]), str(not_evaluated_count)],
    ], colWidths=[28.3 * mm] * 6)
    sev_row.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0d1f4c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("GRID", (0, 0), (-1, -1), 0.4, grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(sev_row)
    if not_evaluated_count:
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f"<i>{not_evaluated_count} check(s) could not be evaluated (e.g. no reputation "
            "provider configured) and are excluded from the score and severity counts above "
            "rather than being treated as passing.</i>", normal))

    story.append(Spacer(1, 12))

    # -----------------------------
    # Positive Security Controls
    # -----------------------------
    if positive_controls:
        story.append(Paragraph("Positive Security Controls", heading))
        for title in positive_controls:
            story.append(Paragraph(f"\u2713 {title}", normal))
        story.append(Spacer(1, 12))

    # -----------------------------
    # Findings
    # -----------------------------

    story.append(
        Paragraph("Security Findings", heading)
    )

    rows = [
        ["Check", "Result"],
        ["HTTPS Enabled", str(d.get("ssl", {}).get("https"))],
        ["Certificate Valid", str(d.get("ssl", {}).get("valid"))],
        ["TLS Version", ", ".join(d.get("ssl", {}).get("tls", []) or []) or "Unknown"],
        ["Security Headers", f"{headers_present}/{total_headers} Present"],
        ["SPF Record", str(d.get("dns", {}).get("SPF"))],
        ["DMARC Record", str(d.get("dns", {}).get("DMARC"))],
        ["DKIM", str(d.get("dns", {}).get("DKIM"))],
        ["Blacklist Status", "Not Evaluated" if not d["reputation"].get("evaluated") else str(d["reputation"].get("blacklisted"))],
        ["HTTP Status", str(d["http"].get("status"))],
        ["Server", str(d["http"].get("server"))],
       ["Technology", (d.get("tech", {}).get("cms") if d.get("tech", {}).get("cms") not in (None, "None") else d.get("tech", {}).get("server", "Unknown"))],
        ["Open Ports", "None exposed" if d.get("ports", {}).get("all_closed", True)
         else f"{len(d.get('ports', {}).get('open_ports', []))} exposed (see below)"],
    ]

    table = Table(rows, colWidths=[60 * mm, 110 * mm])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0d1f4c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("GRID", (0, 0), (-1, -1), 0.4, grey),
        ("BACKGROUND", (0, 1), (0, -1), HexColor("#eef4ff")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(table)

    story.append(Spacer(1, 12))

    # -----------------------------
    # Open Ports (detail — only shown when something is actually exposed)
    # -----------------------------
    open_ports = d.get("ports", {}).get("open_ports", [])
    if open_ports:
        story.append(Paragraph("Exposed Ports", heading))
        port_rows = [["Port", "Service", "Severity", "Why it matters"]] + [
            [str(p["port"]), p["service"], p["severity"].capitalize(), p["reason"]]
            for p in open_ports
        ]
        port_table = Table(port_rows, colWidths=[15 * mm, 25 * mm, 20 * mm, 110 * mm])
        port_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0d1f4c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("GRID", (0, 0), (-1, -1), 0.4, grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(port_table)
        story.append(Spacer(1, 12))

    # -----------------------------
    # Recommendations
    # -----------------------------

    story.append(
        Paragraph("Security Recommendations", heading)
    )

    for item in recommendations:
        story.append(
            Paragraph(item, normal)
        )

    story.append(Spacer(1, 12))

    # -----------------------------
    # Website Information
    # -----------------------------

    story.append(
        Paragraph("Website Information", heading)
    )

    website = Table([
        ["IP Address", str(d["domain"].get("ip"))],
        ["Hosting", str(d["domain"].get("host", "Unknown"))],
        ["Registrar", str(d["domain"].get("registrar"))],
        ["Domain Age", str(d["domain"].get("age"))],
    ], colWidths=[55 * mm, 115 * mm])

    website.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, grey),
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#eef4ff")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))

    story.append(website)

    story.append(Spacer(1, 18))

    # -----------------------------
    # Disclaimer
    # -----------------------------

    story.append(
        Paragraph(
            "Disclaimer",
            heading
        )
    )

    story.append(
        Paragraph(
            """
            This report is generated automatically using publicly observable
            technical indicators. It does not guarantee that a website is
            completely secure or vulnerable. Always perform manual testing
            and obtain authorization before conducting any security
            assessment.
            """,
            normal,
        )
    )

    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "<font color='#666666'><b>Generated by CyberInspect</b><br/>"
            "Website Security Assessment Platform</font>",
            normal,
        )
    )

    doc.build(story)

    return buf.getvalue()