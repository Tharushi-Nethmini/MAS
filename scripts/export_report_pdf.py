from __future__ import annotations

import argparse
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def markdown_to_story(markdown: str):
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
    h3_style = styles["Heading4"]
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

    story = []
    story.append(Paragraph("AI-Based Smart Price Comparison Report", title_style))
    story.append(Paragraph("AI-Based Smart Price Comparison Multi-Agent System", subtitle_style))
    story.append(Spacer(1, 0.18 * cm))

    lines = markdown.splitlines()
    in_code_block = False
    code_block_lang = ""
    code_lines: list[str] = []

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                code_text = "\n".join(code_lines)
                if code_block_lang.lower() == "mermaid":
                    story.append(
                        Paragraph(
                            "Figure: Diagram content is kept in markdown source. "
                            "Use markdown preview for visual graph rendering.",
                            body_style,
                        )
                    )
                else:
                    story.append(Paragraph(_escape_html(code_text).replace("\n", "<br/>"), body_style))
                story.append(Spacer(1, 0.2 * cm))
                code_lines = []
                in_code_block = False
                code_block_lang = ""
            else:
                in_code_block = True
                code_block_lang = stripped.replace("```", "").strip()
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not stripped:
            story.append(Spacer(1, 0.12 * cm))
            continue

        if stripped.startswith("# "):
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(_escape_html(stripped[3:].strip()), h1_style))
            story.append(Spacer(1, 0.12 * cm))
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(_escape_html(stripped[4:].strip()), h2_style))
            story.append(Spacer(1, 0.1 * cm))
            continue
        if stripped.startswith("#### "):
            story.append(Paragraph(_escape_html(stripped[5:].strip()), h3_style))
            story.append(Spacer(1, 0.08 * cm))
            continue

        bullet_match = re.match(r"^[-*]\s+(.*)$", stripped)
        numbered_match = re.match(r"^(\d+\.)\s+(.*)$", stripped)

        if bullet_match:
            story.append(Paragraph(f"&bull; {_escape_html(bullet_match.group(1))}", bullet_style))
            continue
        if numbered_match:
            story.append(
                Paragraph(
                    f"{_escape_html(numbered_match.group(1))} {_escape_html(numbered_match.group(2))}",
                    body_style,
                )
            )
            continue

        story.append(Paragraph(_escape_html(stripped), body_style))

    return story


def export_markdown_to_pdf(input_md: Path, output_pdf: Path) -> None:
    markdown = input_md.read_text(encoding="utf-8")
    story = markdown_to_story(markdown)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="CTSE MAS Technical Report",
    )
    doc.build(story)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export markdown file to PDF")
    parser.add_argument("--input", dest="input_md", help="Input markdown file path")
    parser.add_argument("--output", dest="output_pdf", help="Output PDF file path")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    input_md = Path(args.input_md) if args.input_md else project_root / "docs" / "technical_report_draft.md"
    output_pdf = Path(args.output_pdf) if args.output_pdf else project_root / "docs" / "technical_report_final.pdf"

    if not input_md.exists():
        raise FileNotFoundError(f"Input report not found: {input_md}")

    export_markdown_to_pdf(input_md, output_pdf)
    print(f"PDF generated: {output_pdf}")


if __name__ == "__main__":
    main()
