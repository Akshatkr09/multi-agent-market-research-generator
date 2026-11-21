"""ReportLab PDF compiler for market research reports."""
from pathlib import Path
from typing import Optional
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, HRFlowable,
)
from reportlab.pdfgen import canvas


NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2F6690")
PALE_BLUE = colors.HexColor("#EAF1F7")
DARK = colors.HexColor("#263238")
MID = colors.HexColor("#607D8B")
LIGHT = colors.HexColor("#D9E2EA")


class NumberedCanvas(canvas.Canvas):
    """Canvas that adds accurate 'Page X of Y' footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_number(total_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_page_number(self, total_pages: int):
        width, _ = A4
        self.saveState()
        self.setStrokeColor(LIGHT)
        self.setLineWidth(0.5)
        self.line(18 * mm, 15 * mm, width - 18 * mm, 15 * mm)
        self.setFont("Helvetica", 8)
        self.setFillColor(MID)
        self.drawString(18 * mm, 10 * mm, "Market Research Report | Prepared for analysis")
        self.drawRightString(width - 18 * mm, 10 * mm, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=19, leading=23, textColor=NAVY, alignment=TA_LEFT,
            spaceAfter=5 * mm,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle", parent=base["Normal"], fontSize=9,
            leading=13, textColor=MID, spaceAfter=2 * mm,
        ),
        "h1": ParagraphStyle(
            "ReportH1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=15, leading=19, textColor=NAVY, spaceBefore=7 * mm,
            spaceAfter=3 * mm, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "ReportH2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, textColor=BLUE, spaceBefore=5 * mm,
            spaceAfter=2 * mm, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "ReportBody", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9, leading=14, textColor=DARK, spaceAfter=3 * mm,
        ),
        "bullet": ParagraphStyle(
            "ReportBullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9, leading=13, leftIndent=5 * mm, firstLineIndent=-3 * mm,
            textColor=DARK, spaceAfter=1.5 * mm,
        ),
        "table": ParagraphStyle(
            "ReportTable", parent=base["BodyText"], fontSize=7.5,
            leading=10, textColor=DARK,
        ),
        "small": ParagraphStyle(
            "ReportSmall", parent=base["BodyText"], fontSize=8,
            leading=11, textColor=MID,
        ),
    }


def _inline_markup(text: str) -> str:
    """Escape user content and support simple Markdown bold and italics."""
    safe = escape(text.strip())
    safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
    safe = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", safe)
    return safe


def _parse_markdown_table(lines, styles):
    rows = []
    for line in lines:
        stripped = line.strip().strip("|")
        if not stripped:
            continue
        cells = [cell.strip() for cell in stripped.split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells):
            continue
        rows.append([Paragraph(_inline_markup(cell), styles["table"]) for cell in cells])
    if not rows:
        return None
    column_count = max(len(row) for row in rows)
    for row in rows:
        row.extend([Paragraph("", styles["table"])] * (column_count - len(row)))
    table = Table(rows, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE_BLUE]),
        ("GRID", (0, 0), (-1, -1), 0.35, LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def _markdown_to_story(markdown: str, styles):
    story = []
    lines = (markdown or "").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if "|" in line and line.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            table = _parse_markdown_table(table_lines, styles)
            if table:
                story.extend([Spacer(1, 2 * mm), table, Spacer(1, 3 * mm)])
            continue
        if line.startswith("### "):
            story.append(Paragraph(_inline_markup(line[4:]), styles["h2"]))
        elif line.startswith("## "):
            story.append(Paragraph(_inline_markup(line[3:]), styles["h1"]))
        elif line.startswith("# "):
            story.append(Paragraph(_inline_markup(line[2:]), styles["h1"]))
        elif line.startswith(("- ", "* ")):
            story.append(Paragraph("&#8226; " + _inline_markup(line[2:]), styles["bullet"]))
        else:
            story.append(Paragraph(_inline_markup(line), styles["body"]))
        index += 1
    return story


def _draw_header(canvas_obj, doc):
    canvas_obj.saveState()
    page_width, page_height = A4
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, page_height - 12 * mm, page_width, 12 * mm, fill=1, stroke=0)
    canvas_obj.setFillColor(colors.white)
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.drawString(18 * mm, page_height - 7.5 * mm, "MARKET INTELLIGENCE")
    canvas_obj.setFillColor(MID)
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.drawRightString(page_width - 18 * mm, page_height - 7.5 * mm, "RESEARCH & ANALYSIS")
    canvas_obj.restoreState()


def compile_market_report(
    title: str,
    report_text: str,
    metrics_markdown: str = "",
    output_path: str = "output/market_report.pdf",
    query: Optional[str] = None,
) -> str:
    """Compile report copy and an optional Markdown metrics table into an A4 PDF.

    Returns the absolute path to the generated PDF.
    """
    if not str(title).strip():
        raise ValueError("Report title must not be empty.")
    if not str(report_text).strip() and not str(metrics_markdown).strip():
        raise ValueError("Provide report text or a metrics table.")

    destination = Path(output_path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    styles = _styles()

    doc = SimpleDocTemplate(
        str(destination), pagesize=A4,
        rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=21 * mm, bottomMargin=22 * mm,
        title=title, author="Market Research Generator",
        subject=query or "Market research analysis",
    )

    story = [
        Spacer(1, 3 * mm),
        Paragraph(_inline_markup(title), styles["title"]),
        Paragraph("Market research analysis", styles["subtitle"]),
    ]
    if query:
        story.append(Paragraph(f"<b>Research query:</b> {_inline_markup(query)}", styles["small"]))
    story.extend([
        Paragraph("<b>Document:</b> Market Research Report", styles["small"]),
        Paragraph("<b>Generated:</b> Automatically compiled report", styles["small"]),
        Spacer(1, 4 * mm),
        HRFlowable(width="100%", thickness=1, color=LIGHT, spaceAfter=4 * mm),
    ])

    if report_text.strip():
        story.extend(_markdown_to_story(report_text, styles))
    if metrics_markdown.strip():
        story.append(Paragraph("Financial Summary Statistics", styles["h1"]))
        story.extend(_markdown_to_story(metrics_markdown, styles))

    doc.build(story, onFirstPage=_draw_header, onLaterPages=_draw_header, canvasmaker=NumberedCanvas)
    return str(destination.resolve())


# Friendly alias for callers that prefer a shorter function name.
generate_pdf_report = compile_market_report
