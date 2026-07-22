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

import os
def build_pdf(scan) -> bytes:

    buf = BytesIO()

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

    # -----------------------------
    # Security Headers
    # -----------------------------
    headers_list = d.get("headers", {}).get("headers", [])

    headers_present = sum(1 for h in headers_list if h.get("present"))

    total_headers = len(headers_list)

    # -----------------------------
    # Recommendations
    # -----------------------------
    recommendations = []

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
                <b>{scan.full_url}</b>. The website achieved a security score
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
    # Findings
    # -----------------------------

    story.append(
        Paragraph("Security Findings", heading)
    )

    tls_versions = d.get("ssl", {}).get("tls") or []
    tls_display = ", ".join(tls_versions) if tls_versions else "Unknown"

    tech = d.get("tech", {})
    cms = tech.get("cms")
    tech_display = cms if cms and cms != "None" else tech.get("server", "Unknown")

    rows = [
        ["Check", "Result"],
        ["HTTPS Enabled", str(d.get("ssl", {}).get("https"))],
        ["Certificate Valid", str(d.get("ssl", {}).get("valid"))],
        ["TLS Version", tls_display],
        ["Security Headers", f"{headers_present}/{total_headers} Present"],
        ["SPF Record", str(d.get("dns", {}).get("SPF"))],
        ["DMARC Record", str(d.get("dns", {}).get("DMARC"))],
        ["DKIM", str(d.get("dns", {}).get("DKIM"))],
        ["Blacklist Status", str(d["reputation"].get("blacklisted"))],
        ["HTTP Status", str(d["http"].get("status"))],
        ["Server", str(d["http"].get("server"))],
        ["Technology", str(tech_display)],
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