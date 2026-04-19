from __future__ import annotations

from pathlib import Path


def save_report_pdf(path: str, title: str, content: str) -> str:
    """Save plain-text report content as a PDF and return absolute path."""

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("reportlab is required for PDF export") from exc

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=9,
        leading=11,
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

    story = [Paragraph(title, title_style), Spacer(1, 0.35 * cm), Preformatted(content, body_style)]
    doc.build(story)
    return str(output.resolve())
