"""
Jinja2 Report Template Engine

Renders validated financial data into formatted CBN regulatory
returns using Jinja2 HTML templates. Supports:
    - Capital Adequacy Return (CAR)
    - PDF generation via ReportLab
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from datetime import datetime
import os


# ── Color palette ────────────────────────────────────────────────────
NAVY = HexColor("#0F2C4D")
TEAL = HexColor("#1ABC9C")
RED = HexColor("#E74C3C")
WHITE = HexColor("#FFFFFF")
LIGHT_GRAY = HexColor("#F8F9FA")
DARK_GRAY = HexColor("#2C3E50")


def compute_ratios(data):
    """Compute capital ratios from raw data."""
    cet1 = float(data["cet1_capital"])
    at1 = float(data["additional_tier1"])
    t2 = float(data["tier2_capital"])
    rwa = float(data["total_rwa"])

    tier1 = cet1 + at1
    total_capital = tier1 + t2

    return {
        "cet1_capital": cet1,
        "additional_tier1": at1,
        "tier1_capital": tier1,
        "tier2_capital": t2,
        "total_capital": total_capital,
        "total_rwa": rwa,
        "credit_rwa": float(data["credit_rwa"]),
        "market_rwa": float(data["market_rwa"]),
        "operational_rwa": float(data["operational_rwa"]),
        "cet1_ratio": round((cet1 / rwa) * 100, 2),
        "tier1_ratio": round((tier1 / rwa) * 100, 2),
        "total_car": round((total_capital / rwa) * 100, 2),
    }


def render_html_report(data, output_path="output/car_report.html"):
    """Render the Capital Adequacy Return as an HTML file."""
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html"]),
    )

    ratios = compute_ratios(data)
    context = {
        "bank_name": data["bank_name"],
        "report_date": data["report_date"],
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        **ratios,
    }

    template = env.get_template("car_report.html")
    html = template.render(**context)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ HTML report saved: {output_path}")
    return output_path


def generate_pdf_report(data, output_path="output/car_report.pdf"):
    """Generate a PDF Capital Adequacy Return."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    ratios = compute_ratios(data)
    bank_name = data["bank_name"]
    report_date = data["report_date"]

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=25 * mm,
        leftMargin=25 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=18,
        textColor=NAVY,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=NAVY,
        spaceBefore=16,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        "FooterText",
        parent=styles["Normal"],
        fontSize=8,
        textColor=DARK_GRAY,
    ))

    elements = []

    # Header
    elements.append(Paragraph(
        "CAPITAL ADEQUACY RETURN", styles["ReportTitle"]
    ))
    elements.append(Paragraph(
        f"<b>{bank_name}</b>", styles["Heading3"]
    ))
    elements.append(Paragraph(
        f"Report Date: {report_date} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(
        width="100%", thickness=2, color=TEAL, spaceAfter=12
    ))

    # Capital Structure table
    elements.append(Paragraph("A. Capital Structure", styles["SectionHeader"]))

    capital_data = [
        ["Component", "Amount (₦'000)", "% of RWA"],
        ["CET1 Capital", f"{ratios['cet1_capital']:,.0f}",
         f"{ratios['cet1_ratio']:.2f}%"],
        ["Additional Tier 1", f"{ratios['additional_tier1']:,.0f}", "—"],
        ["Total Tier 1 Capital", f"{ratios['tier1_capital']:,.0f}",
         f"{ratios['tier1_ratio']:.2f}%"],
        ["Tier 2 Capital", f"{ratios['tier2_capital']:,.0f}", "—"],
        ["Total Regulatory Capital", f"{ratios['total_capital']:,.0f}",
         f"{ratios['total_car']:.2f}%"],
    ]

    capital_table = Table(capital_data, colWidths=[200, 150, 100])
    capital_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT_GRAY),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, 0), 1, TEAL),
        ("LINEBELOW", (0, -1), (-1, -1), 1, NAVY),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#DEE2E6")),
    ]))
    elements.append(capital_table)
    elements.append(Spacer(1, 16))

    # RWA Breakdown table
    elements.append(Paragraph(
        "B. Risk-Weighted Assets", styles["SectionHeader"]
    ))

    rwa_data = [
        ["Category", "Amount (₦'000)", "% of Total"],
        ["Credit Risk RWA", f"{ratios['credit_rwa']:,.0f}",
         f"{(ratios['credit_rwa'] / ratios['total_rwa'] * 100):.1f}%"],
        ["Market Risk RWA", f"{ratios['market_rwa']:,.0f}",
         f"{(ratios['market_rwa'] / ratios['total_rwa'] * 100):.1f}%"],
        ["Operational Risk RWA", f"{ratios['operational_rwa']:,.0f}",
         f"{(ratios['operational_rwa'] / ratios['total_rwa'] * 100):.1f}%"],
        ["Total RWA", f"{ratios['total_rwa']:,.0f}", "100.0%"],
    ]

    rwa_table = Table(rwa_data, colWidths=[200, 150, 100])
    rwa_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT_GRAY),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#DEE2E6")),
    ]))
    elements.append(rwa_table)
    elements.append(Spacer(1, 16))

    # Compliance Summary
    elements.append(Paragraph(
        "C. CBN Compliance Status", styles["SectionHeader"]
    ))

    min_car = 10.0  # non-D-SIB default
    status = "COMPLIANT" if ratios["total_car"] >= min_car else "NON-COMPLIANT"
    status_color = TEAL if status == "COMPLIANT" else RED

    compliance_data = [
        ["Ratio", "Actual", "CBN Minimum", "Status"],
        ["CET1 Ratio", f"{ratios['cet1_ratio']:.2f}%", "5.00%",
         "✓" if ratios["cet1_ratio"] >= 5.0 else "✗ BREACH"],
        ["Tier 1 Ratio", f"{ratios['tier1_ratio']:.2f}%", "6.50%",
         "✓" if ratios["tier1_ratio"] >= 6.5 else "✗ BREACH"],
        ["Total CAR", f"{ratios['total_car']:.2f}%", "10.00%",
         "✓" if ratios["total_car"] >= 10.0 else "✗ BREACH"],
    ]

    comp_table = Table(compliance_data, colWidths=[120, 100, 100, 130])
    comp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#DEE2E6")),
    ]))
    elements.append(comp_table)
    elements.append(Spacer(1, 20))

    # Footer
    elements.append(HRFlowable(
        width="100%", thickness=1, color=HexColor("#DEE2E6"),
        spaceAfter=8
    ))
    elements.append(Paragraph(
        "This report was generated programmatically. "
        "For official regulatory submissions, verify against CBN Form CAR 001.",
        styles["FooterText"]
    ))

    doc.build(elements)
    print(f"✓ PDF report saved: {output_path}")
    return output_path
