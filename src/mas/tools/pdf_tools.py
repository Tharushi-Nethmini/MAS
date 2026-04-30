from __future__ import annotations

from pathlib import Path
import re


def save_report_pdf(path: str, title: str, content: str) -> str:
    """Save markdown-like report content as a formatted PDF and return absolute path."""

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("reportlab is required for PDF export") from exc

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    def _escape_html(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=10,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10,
    )
    h1_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0B3C5D"),
        spaceBefore=8,
        spaceAfter=4,
    )
    h2_style = ParagraphStyle(
        "SubSectionHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1D4E89"),
        spaceBefore=6,
        spaceAfter=3,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#111827"),
        spaceAfter=2,
    )
    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=body_style,
        leftIndent=12,
        bulletIndent=2,
    )

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title=title,
    )

    story = []
    story.append(Paragraph(_escape_html(title), title_style))
    story.append(Paragraph("AI-Based Smart Price Comparison Multi-Agent System", subtitle_style))
    story.append(Spacer(1, 0.18 * cm))
    lines = content.splitlines()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 0.12 * cm))
            continue
        if stripped.startswith("# "):
            # Skip markdown title because we already render a document title block.
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(_escape_html(stripped[3:].strip()), h1_style))
            story.append(Spacer(1, 0.15 * cm))
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(_escape_html(stripped[4:].strip()), h2_style))
            story.append(Spacer(1, 0.1 * cm))
            continue

        bullet_match = re.match(r"^[-*]\s+(.*)$", stripped)
        if bullet_match:
            story.append(Paragraph(f"&bull; {_escape_html(bullet_match.group(1))}", bullet_style))
            continue

        numbered_match = re.match(r"^(\d+\.)\s+(.*)$", stripped)
        if numbered_match:
            story.append(
                Paragraph(
                    f"{_escape_html(numbered_match.group(1))} {_escape_html(numbered_match.group(2))}",
                    body_style,
                )
            )
            continue

        story.append(Paragraph(_escape_html(stripped), body_style))

    doc.build(story)
    return str(output.resolve())
