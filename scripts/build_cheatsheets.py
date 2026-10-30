"""Build six printable, one-page PDFs from the committed sheet content.
Run: uv run --group docs python scripts/build_cheatsheets.py
"""

import json
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import BaseDocTemplate, Frame, KeepTogether, PageTemplate, Paragraph, Spacer

from common.config import ROOT


def build():
    folder = ROOT / "cheatsheets"
    sheets = json.loads((folder / "sheets.json").read_text())
    body = ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        spaceAfter=7,
        textColor=colors.HexColor("#243449"),
        alignment=TA_LEFT,
    )
    heading = ParagraphStyle(
        "heading",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        spaceBefore=8,
        spaceAfter=8,
        textColor=colors.HexColor("#006E75"),
    )
    for name, title, subtitle, sections in sheets:
        path = folder / (name + ".pdf")

        def page(canvas, doc, title=title, subtitle=subtitle):
            canvas.setFillColor(colors.HexColor("#122B44"))
            canvas.rect(0, 688, 612, 104, fill=1, stroke=0)
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 23)
            canvas.drawString(36, 746, title)
            canvas.setFont("Helvetica", 11)
            canvas.drawString(36, 721, subtitle)
            canvas.setFillColor(colors.HexColor("#536779"))
            canvas.setFont("Helvetica", 8)
            canvas.drawString(
                36, 29, "LUMEN LABS / SYNTHETIC COURSE / MCP 2026-07-28 / CHECKED 2026-10-30"
            )
            canvas.drawRightString(576, 29, "1 / 1")

        frames = [
            Frame(x, 50, 258, 624, leftPadding=0, rightPadding=7, topPadding=0, bottomPadding=0)
            for x in [36, 318]
        ]
        doc = BaseDocTemplate(
            str(path),
            pagesize=(612, 792),
            title=title,
            author="Lumen MCP course",
            pageCompression=1,
        )
        doc.addPageTemplates(PageTemplate(id="sheet", frames=frames, onPage=page))
        story = []
        for label, lines in sections:
            block = [Paragraph(escape(label), heading)]
            block += [Paragraph(escape(line), body) for line in lines]
            block.append(Spacer(1, 6))
            story.append(KeepTogether(block))
        doc.build(story)
        reader = PdfReader(path)
        if len(reader.pages) != 1 or not reader.pages[0].extract_text():
            raise ValueError(f"{name}: must be one readable page")
        print(f"PASS one-page PDF {path.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
