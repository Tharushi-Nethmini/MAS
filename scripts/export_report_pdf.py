from __future__ import annotations

import argparse
from pathlib import Path
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def markdown_to_story(markdown: str):
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    h1_style = styles["Heading1"]
    h2_style = styles["Heading2"]
    h3_style = styles["Heading3"]
    body_style = styles["BodyText"]
    code_style = ParagraphStyle(
        "CodeBlock",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8,
        leading=10,
    )

    story = []
    lines = markdown.splitlines()
    in_code_block = False
    code_block_lang = ""
    code_lines: list[str] = []

    for raw_line in lines:
        line = raw_line.rstrip("\n")

        if line.strip().startswith("```"):
            if in_code_block:
                code_text = "\n".join(code_lines)
                if code_block_lang.lower() == "mermaid":
                    story.append(
                        Paragraph(
                            "Figure: Diagram content is maintained in markdown source. "
                            "For visual diagram rendering, open docs/architecture.md in VS Code preview.",
                            body_style,
                        )
                    )
                else:
                    story.append(Preformatted(code_text, code_style))
                story.append(Spacer(1, 0.25 * cm))
                code_lines = []
                in_code_block = False
                code_block_lang = ""
            else:
                in_code_block = True
                code_block_lang = line.strip().replace("```", "").strip()
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not line.strip():
            story.append(Spacer(1, 0.2 * cm))
            continue

        if line.startswith("# "):
            story.append(Paragraph(_escape_html(line[2:].strip()), title_style))
            story.append(Spacer(1, 0.35 * cm))
            continue
        if line.startswith("## "):
            story.append(Paragraph(_escape_html(line[3:].strip()), h1_style))
            story.append(Spacer(1, 0.2 * cm))
            continue
        if line.startswith("### "):
            story.append(Paragraph(_escape_html(line[4:].strip()), h2_style))
            story.append(Spacer(1, 0.15 * cm))
            continue
        if line.startswith("#### "):
            story.append(Paragraph(_escape_html(line[5:].strip()), h3_style))
            story.append(Spacer(1, 0.1 * cm))
            continue

        bullet_match = re.match(r"^(\s*[-*]\s+)(.*)$", line)
        numbered_match = re.match(r"^(\s*\d+\.\s+)(.*)$", line)

        if bullet_match:
            text = bullet_match.group(2)
            story.append(Paragraph(f"• {_escape_html(text)}", body_style))
            continue

        if numbered_match:
            prefix = numbered_match.group(1).strip()
            text = numbered_match.group(2)
            story.append(Paragraph(f"{_escape_html(prefix)} {_escape_html(text)}", body_style))
            continue

        story.append(Paragraph(_escape_html(line), body_style))

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
    input_md = (
        Path(args.input_md)
        if args.input_md
        else project_root / "docs" / "technical_report_draft.md"
    )
    output_pdf = (
        Path(args.output_pdf)
        if args.output_pdf
        else project_root / "docs" / "technical_report_final.pdf"
    )

    if not input_md.exists():
        raise FileNotFoundError(f"Input report not found: {input_md}")

    export_markdown_to_pdf(input_md, output_pdf)
    print(f"PDF generated: {output_pdf}")


if __name__ == "__main__":
    main()
