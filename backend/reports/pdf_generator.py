from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

def build_pdf(scan) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20*mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("t", parent=styles["Title"], textColor=colors.HexColor("#0d1f4c"))
    story = [Paragraph("🛡️ CyberInspect Security Report", title),
             Paragraph(f"<b>Website:</b> {scan.full_url}", styles["Normal"]),
             Paragraph(f"<b>Score:</b> {scan.score}/100 &nbsp; "
                       f"<b>Risk:</b> {scan.risk_level}", styles["Normal"]),
             Spacer(1, 10)]
    d = scan.result
    rows = [["Check", "Result"],
            ["HTTPS", d["ssl"].get("https")],
            ["Cert Valid", d["ssl"].get("valid")],
            ["Issuer", d["ssl"].get("issuer")],
            ["Headers Present", sum(1 for h in d["headers"]["headers"] if h["present"])],
            ["SPF", d["dns"].get("SPF")], ["DMARC", d["dns"].get("DMARC")],
            ["Reputation", d["reputation"].get("summary")]]
    t = Table([[str(c) for c in r] for r in rows], colWidths=[70*mm, 100*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0d1f4c")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e4ebf5")),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    story.append(Paragraph("<font size=8 color='#8a9bc4'>Assessment based on observable "
        "technical indicators only. Scan only sites you are authorized to assess.</font>",
        styles["Normal"]))
    doc.build(story)
    return buf.getvalue()