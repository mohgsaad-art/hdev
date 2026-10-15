# STATUS: NEW (PR 8, Bob to review). the Excel renderer for the Step 8 report (openpyxl, pure/offline).
#
# build_xlsx(sections, *, illustrative) writes the 9 assembled sections (from report/builder.py) into a
# workbook with ONE sheet per section, each sheet NAMED for its section title (trimmed to openpyxl's
# 31-char sheet-name limit via SHEET_NAMES), and returns the raw .xlsx bytes. §0: pure function, no
# network, no file IO beyond the in-memory buffer.
#
# watermark: when illustrative=True, the EXACT WATERMARK_TEXT is written as a clearly-visible banner in
# the first row (A1) of EVERY sheet, so the illustrative label is on every sheet. the section title and
# its two-column rows follow below it. real mode (illustrative=False) omits the banner.
from io import BytesIO
from typing import Any, Mapping, Sequence

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from .builder import SECTION_TITLES, WATERMARK_TEXT

# openpyxl caps sheet names at 31 chars and forbids a few characters. these short, unique names map
# 1:1 to SECTION_TITLES in order and stay well under the limit while naming each section clearly.
SHEET_NAMES: Sequence[str] = (
    "1 Summary",
    "2 Fleet & inputs",
    "3 Energy",
    "4 Charging",
    "5 Grid & flexibility",
    "6 Total cost",
    "7 CO2",
    "8 Plan",
    "9 Inputs & sources",
)

# visual styling for the watermark banner + the section-title row.
_WATERMARK_FILL = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")
_WATERMARK_FONT = Font(bold=True, color="856404")
_TITLE_FONT = Font(bold=True, size=13)
_LABEL_FONT = Font(bold=True)


def build_xlsx(sections: Sequence[Mapping[str, Any]], *, illustrative: bool) -> bytes:
    # render the assembled sections to .xlsx bytes. pure: writes to an in-memory buffer only.
    workbook = Workbook()
    # drop the default sheet openpyxl creates; we add one per section explicitly.
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    for index, section in enumerate(sections):
        # pick the short sheet name by position; fall back to a truncated title if positions ever grow.
        if index < len(SHEET_NAMES):
            sheet_name = SHEET_NAMES[index]
        else:
            sheet_name = str(section.get("title", f"Section {index + 1}"))[:31]
        ws = workbook.create_sheet(title=sheet_name)

        current_row = 1
        if illustrative:
            # the EXACT watermark banner on every sheet, filled so it is clearly visible.
            cell = ws.cell(row=current_row, column=1, value=WATERMARK_TEXT)
            cell.font = _WATERMARK_FONT
            cell.fill = _WATERMARK_FILL
            banner_b = ws.cell(row=current_row, column=2, value=WATERMARK_TEXT)
            banner_b.font = _WATERMARK_FONT
            banner_b.fill = _WATERMARK_FILL
            current_row += 2

        # the full section title (the heading inside the sheet).
        title_cell = ws.cell(row=current_row, column=1, value=str(section.get("title", "")))
        title_cell.font = _TITLE_FONT
        current_row += 1

        # the two-column rows.
        for row in section.get("rows") or []:
            if not isinstance(row, Mapping):
                continue
            label_cell = ws.cell(row=current_row, column=1, value=str(row.get("label", "")))
            label_cell.font = _LABEL_FONT
            label_cell.alignment = Alignment(vertical="top", wrap_text=False)
            value_cell = ws.cell(row=current_row, column=2, value=str(row.get("value", "")))
            value_cell.alignment = Alignment(vertical="top", wrap_text=True)
            current_row += 1

        # a sensible column width so labels/values are readable when opened.
        ws.column_dimensions["A"].width = 34
        ws.column_dimensions["B"].width = 60

    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


# a construction-time sanity check so SHEET_NAMES can never drift out of step with the 9 titles.
assert len(SHEET_NAMES) == len(SECTION_TITLES), "SHEET_NAMES must have one entry per section title"
