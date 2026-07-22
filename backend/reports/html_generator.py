def build_html(scan) -> str:
    d = scan.result
    print(d.keys())
    hdr_rows = "".join(f"<tr><td>{h['name']}</td><td>{'Present' if h['present'] else 'Missing'}</td></tr>"
                       for h in d["headers"]["headers"])
    return f"""<html><head><meta charset='utf-8'><title>CyberInspect Report</title>
    <style>body{{font-family:Arial;padding:40px;color:#0d1f4c}}h1{{color:#00a3b5}}
    table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #e4ebf5;padding:8px}}
    th{{background:#0d1f4c;color:#fff}}</style></head><body>
    <h1>🛡️ CyberInspect Security Report</h1>
    <p><b>{scan.full_url}</b> — Score {scan.score}/100 ({scan.risk_level})</p>
    <h3>Security Headers</h3><table>{hdr_rows}</table>
    <p style='font-size:12px;color:#8a9bc4;margin-top:20px'>
    Assessment based on observable technical indicators only.</p></body></html>"""