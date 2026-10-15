# STATUS: NEW (PR 8, Bob to review). offline tests for the Step 8 report export.
# no socket, no network, no AI provider. follows tests/test_run.py / test_scenarios_audit.py patterns.
#
# what these assert (both direct unit calls on report.* and end-to-end via TestClient):
#   - the Excel path FULLY: the workbook opens, has one NAMED sheet per section in the 9-section order,
#     carries the EXACT watermark text on EVERY sheet (demo), and its numbers match the results JSON
#     (a KPI, a TCO category, the inputs_summary total).
#   - the §8 guard on BOTH formats: iterate every registry collapsed/hidden field id+label and assert
#     NONE appears in the rendered content (xlsx cells / assembled sections), while the known OPEN field
#     labels DO appear, and the source table in section 9 is counts-only.
#   - the PDF path: bytes start with %PDF and are non-trivial; the assembled-sections content (what the
#     PDF renders) contains the 9 section titles + the watermark; the §8 guard holds on it too.
#   - real mode (illustrative=False): no watermark, unavailable fields read "Not yet available".
#   - the endpoint returns 200 with the right Content-Type + attachment filename for pdf and excel, and
#     a bad ?format= returns a 400.
import io
import os

import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook

import report
from hdev.report_api import build_report_response
from hdev.run_api import build_run_payload
from hdev.server import create_app
from report.builder import NOT_AVAILABLE, SECTION_TITLES, WATERMARK_TEXT, sections_text
from src.registry import FIELDS

PDF_MEDIA_TYPE = "application/pdf"
XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# ---------------------------------------------------------------------------
# helpers that gather the demo inputs the way the chokepoint does.
# ---------------------------------------------------------------------------
def _demo_results():
    status, payload = build_run_payload("demo", {"levers": {}}, log_run=False)
    assert status == 200
    return payload


def _demo_audit():
    import audit

    return audit.source_type_tallies()


def _demo_open_fields():
    from hdev.intake_api import build_intake_payload

    payload = build_intake_payload("demo")
    fields = []
    for section in payload.get("sections", []):
        fields.extend(section.get("fields", []))
    return fields


def _workbook_text(data: bytes) -> str:
    # every cell value across every sheet, joined - the client-visible content of the workbook.
    wb = load_workbook(io.BytesIO(data))
    parts = []
    for name in wb.sheetnames:
        ws = wb[name]
        for row in ws.iter_rows(values_only=True):
            for cell in row:
                if cell is not None:
                    parts.append(str(cell))
    return "\n".join(parts)


@pytest.fixture()
def client():
    # default environment -> demo mode. fresh app per test resets the project store.
    return TestClient(create_app())


# ---------------------------------------------------------------------------
# the 9 sections, order + presence, via assemble_sections (the single source of truth).
# ---------------------------------------------------------------------------
def test_assemble_sections_has_nine_titles_in_order():
    sections = report.assemble_sections(
        _demo_results(), _demo_audit(), None, _demo_open_fields(), illustrative=True
    )
    assert [s["title"] for s in sections] == list(SECTION_TITLES)
    assert len(sections) == 9


# ---------------------------------------------------------------------------
# Excel path, FULLY.
# ---------------------------------------------------------------------------
def test_xlsx_has_one_named_sheet_per_section_in_order():
    data = report.build_xlsx(
        _demo_results(), _demo_audit(), None, _demo_open_fields(), illustrative=True
    )
    assert data[:2] == b"PK"  # a zip/xlsx container
    wb = load_workbook(io.BytesIO(data))
    assert wb.sheetnames == [
        "1 Summary",
        "2 Fleet & inputs",
        "3 Energy",
        "4 Charging",
        "5 Grid & flexibility",
        "6 Total cost",
        "7 CO2",
        "8 Plan",
        "9 Inputs & sources",
    ]


def test_xlsx_watermark_on_every_sheet_in_demo():
    data = report.build_xlsx(
        _demo_results(), _demo_audit(), None, _demo_open_fields(), illustrative=True
    )
    wb = load_workbook(io.BytesIO(data))
    for name in wb.sheetnames:
        ws = wb[name]
        # the EXACT watermark text is the banner in A1 of every sheet.
        assert ws["A1"].value == WATERMARK_TEXT, f"missing watermark on sheet {name}"


def test_xlsx_numbers_match_results_json():
    results = _demo_results()
    data = report.build_xlsx(results, _demo_audit(), None, _demo_open_fields(), illustrative=True)
    text = _workbook_text(data)

    # a KPI: battery per truck (310 in the default demo run) appears verbatim.
    battery = results["kpis"]["battery_kwh"]
    assert f"{round(float(battery)):,}" in text

    # a TCO category: the first category name (Owning) is present.
    assert results["tco"]["categories"][0]["name"] in text

    # the inputs_summary total (106) is present in section 2.
    total = results["inputs_summary"]["total"]
    assert f"{round(float(total)):,}" in text


# ---------------------------------------------------------------------------
# §8 guard on the EXCEL: no collapsed/hidden field id/label; open labels DO appear; counts-only table.
# ---------------------------------------------------------------------------
def test_xlsx_section8_no_hidden_or_collapsed_field_names():
    data = report.build_xlsx(
        _demo_results(), _demo_audit(), None, _demo_open_fields(), illustrative=True
    )
    text = _workbook_text(data)

    # iterate EVERY registry collapsed/hidden field and assert neither its id nor its label appears.
    for field in FIELDS:
        if getattr(field, "visibility", None) == "open":
            continue
        assert field.id not in text, f"collapsed/hidden field id leaked: {field.id}"
        label = getattr(field, "label", None)
        if label:
            assert label not in text, f"collapsed/hidden field label leaked: {label}"

    # the known OPEN field labels DO appear (open fields are the only ones the report may name).
    open_labels = [f["label"] for f in _demo_open_fields()]
    assert any(lbl in text for lbl in open_labels)
    assert "Shift end" in text  # an open field we know is in the sample case


def test_xlsx_source_table_is_counts_only():
    # the audit source-table row labels are source TYPES (file names / plain words), never a field name.
    audit_table = _demo_audit()
    data = report.build_xlsx(
        _demo_results(), audit_table, None, _demo_open_fields(), illustrative=True
    )
    text = _workbook_text(data)
    for row in audit_table["rows"]:
        assert str(row["source_type"]) in text
    # the server total appears in section 9.
    assert str(audit_table["total"]) in text


# ---------------------------------------------------------------------------
# PDF path.
# ---------------------------------------------------------------------------
def test_pdf_is_a_real_nontrivial_pdf():
    data = report.build_pdf(
        _demo_results(), _demo_audit(), None, _demo_open_fields(), illustrative=True
    )
    assert data[:5] == b"%PDF-"
    assert len(data) > 2000  # a real multi-section document, not an empty shell


def test_pdf_content_has_nine_titles_and_watermark_and_passes_guard():
    # the PDF renders the assembled sections; introspect that content (reportlab draws exactly it).
    results = _demo_results()
    sections = report.assemble_sections(
        results, _demo_audit(), None, _demo_open_fields(), illustrative=True
    )
    content = sections_text(sections)

    # all 9 section titles are in the rendered content.
    for title in SECTION_TITLES:
        assert title in content

    # the watermark text is stamped on every PDF page (and shown as an in-flow note); assert the
    # renderer embeds the exact string in the drawn page content.
    data = report.build_pdf(results, _demo_audit(), None, _demo_open_fields(), illustrative=True)
    raw = data.decode("latin-1", errors="ignore")
    assert WATERMARK_TEXT in raw

    # the watermark is drawn on EVERY page: at least one occurrence per page (one /MediaBox per page).
    page_count = raw.count("/MediaBox")
    assert page_count >= 1
    assert raw.count(WATERMARK_TEXT) >= page_count

    # the §8 guard holds on the PDF content.
    assert report.assert_no_hidden_fields(sections) is True


def test_pdf_section8_guard_on_content():
    sections = report.assemble_sections(
        _demo_results(), _demo_audit(), None, _demo_open_fields(), illustrative=True
    )
    content = sections_text(sections)
    for field in FIELDS:
        if getattr(field, "visibility", None) == "open":
            continue
        assert field.id not in content
        label = getattr(field, "label", None)
        if label:
            assert label not in content


# ---------------------------------------------------------------------------
# real mode: no watermark, "Not yet available" for unavailable fields.
# ---------------------------------------------------------------------------
def test_real_mode_has_no_watermark_and_not_available():
    status, data, media_type, filename = build_report_response("real", "excel", {})
    assert status == 200
    wb = load_workbook(io.BytesIO(data))
    # no watermark banner in real mode: A1 of the first sheet is the section title, not the watermark.
    assert wb["1 Summary"]["A1"].value != WATERMARK_TEXT
    text = _workbook_text(data)
    assert WATERMARK_TEXT not in text
    # unavailable results render the literal "Not yet available" rather than an invented number.
    assert NOT_AVAILABLE in text


def test_real_mode_pdf_has_no_watermark():
    status, data, media_type, filename = build_report_response("real", "pdf", {})
    assert status == 200
    assert data[:5] == b"%PDF-"
    raw = data.decode("latin-1", errors="ignore")
    assert WATERMARK_TEXT not in raw
    # the 9 section titles still render in real mode (the report is produced, not 404'd).
    assert SECTION_TITLES[0] in raw


# ---------------------------------------------------------------------------
# the endpoint: content-type + attachment filename for both formats; bad format -> 400.
# ---------------------------------------------------------------------------
def test_endpoint_pdf_content_type_and_attachment(client):
    resp = client.get("/api/report?format=pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == PDF_MEDIA_TYPE
    assert "attachment" in resp.headers["content-disposition"]
    assert "hdev-report.pdf" in resp.headers["content-disposition"]
    assert resp.content[:5] == b"%PDF-"


def test_endpoint_excel_content_type_and_attachment(client):
    resp = client.get("/api/report?format=excel")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == XLSX_MEDIA_TYPE
    assert "attachment" in resp.headers["content-disposition"]
    assert "hdev-report.xlsx" in resp.headers["content-disposition"]
    assert resp.content[:2] == b"PK"


def test_endpoint_post_with_results_body(client):
    # the UI posts the current results; the report is built from them. use a real demo run as the body.
    results = _demo_results()
    resp = client.post("/api/report?format=excel", json={"results": results})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == XLSX_MEDIA_TYPE
    assert resp.content[:2] == b"PK"


def test_endpoint_bad_format_is_400(client):
    resp = client.get("/api/report?format=docx")
    assert resp.status_code == 400
    assert resp.json()["ok"] is False
