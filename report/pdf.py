# STATUS: NEW (PR 8, Bob to review). the PDF renderer for the Step 8 report (reportlab, pure/offline).
#
# build_pdf(sections, *, illustrative) renders the 9 assembled sections (from report/builder.py) into a
# single PDF and returns the raw bytes. §0: pure function, no network, no file IO beyond the in-memory
# buffer. reportlab is pure Python and runs with no system libraries, so this path is fully testable
# offline in the sandbox.
#
# layout: each section is a titled block (the section title as a heading) followed by a simple two-
# column table of its {label, value} rows. the document flows across as many pages as needed.
#
# watermark: when illustrative=True, EVERY page gets the EXACT WATERMARK_TEXT drawn as a light diagonal
# across the page (via an onPage callback that runs for every page reportlab lays out), plus a footer
# band carrying the same text, so the illustrative label is visible on each page. real mode
# (illustrative=False) omits the watermark entirely.
from io import BytesIO
from typing import Any, Dict, List, Mapping, Sequence

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .builder import WATERMARK_TEXT


def _watermark_callback(illustrative: bool):
    # returns an onPage(canvas, doc) callback that stamps the illustrative watermark on EVERY page.
    # a no-op when not illustrative (real mode has no watermark).
    def _draw(canvas, doc):
        if not illustrative:
            return
        width, height = A4
        canvas.saveState()
        # a light diagonal watermark across the middle of the page.
        canvas.setFont("Helvetica-Bold", 34)
        canvas.setFillColor(colors.Color(0.85, 0.85, 0.85))
        canvas.translate(width / 2.0, height / 2.0)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, WATERMARK_TEXT)
        canvas.restoreState()
        # a solid footer band with the same text so it is clearly readable on every page.
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(width / 2.0, 10 * mm, WATERMARK_TEXT)
        canvas.restoreState()

    return _draw


def build_pdf(sections: Sequence[Mapping[str, Any]], *, illustrative: bool) -> bytes:
    # render the assembled sections to PDF bytes. pure: writes to an in-memory buffer only.
    buffer = BytesIO()

    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="HDEV report",
        # keep the page content streams UNCOMPRESSED so the rendered text (section titles, the
        # watermark, every row) is introspectable in the raw bytes. this lets the offline tests verify
        # the actual drawn content + the §8 guard against the real PDF without a text-extraction
        # dependency (none is available in-sandbox). the file stays small for a text report.
        pageCompression=0,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates(
        [PageTemplate(id="main", frames=[frame], onPage=_watermark_callback(illustrative))]
    )

    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        spaceBefore=10,
        spaceAfter=6,
        alignment=TA_LEFT,
    )
    label_style = ParagraphStyle("CellLabel", parent=styles["BodyText"], fontSize=9, leading=12)
    value_style = ParagraphStyle("CellValue", parent=styles["BodyText"], fontSize=9, leading=12)
    title_style = ParagraphStyle(
        "DocTitle", parent=styles["Title"], fontSize=18, spaceAfter=4
    )
    note_style = ParagraphStyle(
        "DocNote", parent=styles["BodyText"], fontSize=9, textColor=colors.grey, spaceAfter=12
    )

    story: List[Any] = [Paragraph("HDEV report", title_style)]
    if illustrative:
        # a visible in-flow note too (the watermark is additionally stamped on every page).
        story.append(Paragraph(WATERMARK_TEXT, note_style))

    for section in sections:
        story.append(Paragraph(str(section.get("title", "")), heading_style))
        rows = section.get("rows") or []
        table_data: List[List[Any]] = []
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            label = Paragraph(str(row.get("label", "")), label_style)
            value = Paragraph(str(row.get("value", "")), value_style)
            table_data.append([label, value])
        if not table_data:
            table_data.append([Paragraph("", label_style), Paragraph("", value_style)])
        table = Table(table_data, colWidths=[doc.width * 0.42, doc.width * 0.58])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 6))

    doc.build(story)
    return buffer.getvalue()
