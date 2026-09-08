from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

REPORT_DIR = Path(__file__).resolve().parent.parent / "uploads"
REPORT_DIR.mkdir(exist_ok=True)

def create_pdf_report(item):
    result = item["result"]
    path = REPORT_DIR / f"report_{item['id']}.pdf"

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = [
        Paragraph("IPsec AI Analyzer — Security Report", styles["Title"]),
        Spacer(1, 10),
        Paragraph(f"File: {item['filename']}", styles["BodyText"]),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph(f"<b>Security Score:</b> {result['score']}/100", styles["Heading2"]),
        Paragraph(f"<b>Risk:</b> {result['risk']}", styles["BodyText"]),
        Paragraph(result["summary"], styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Checks", styles["Heading2"])
    ]

    rows = [["Check", "Status", "Severity", "Detail"]]
    for c in result["checks"]:
        rows.append([c["name"], c["status"], c["severity"].upper(), c["detail"]])
    table = Table(rows, colWidths=[105, 55, 55, 300])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
    ]))
    story += [table, Spacer(1, 14), Paragraph("Recommendations", styles["Heading2"])]

    for r in result["recommendations"]:
        story.append(Paragraph(f"<b>{r['priority']} — {r['title']}</b>: {r['text']}", styles["BodyText"]))
        story.append(Spacer(1, 5))

    doc.build(story)
    return path
