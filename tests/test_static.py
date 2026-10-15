# STATUS: NEW (PR 2, Bob to review). offline tests for the Step 2 static UI shell (index.html/css/js).
# all via fastapi.testclient.TestClient against the real StaticFiles mount - no socket, no network.
#
# what these assert:
#   - GET / serves the shell HTML with the literal `[TOOL NAME]` and "Fleet electrification assistant"
#     and NO real product/brand name.
#   - GET /css/app.css is 200 and uses @font-face with LOCAL /fonts paths only (no external font/CDN).
#   - GET /js/app.js is 200 and hard-codes NO section display_name and no literal registry count.
#   - GET /fonts/OFL.txt is 200 (the OFL licence ships with the self-hosted fonts).
#   - §8: none of the served HTML/CSS/JS leak `maps_to` or any collapsed-field id/label.
import re

import pytest
from fastapi.testclient import TestClient

from hdev.intake_api import OPENING_LINE
from hdev.server import create_app
from src.registry import (
    SECTIONS,
    counted_only_fields,
)
from src.registry.registry import FIELDS

# real brand names that must NEVER appear in the client (the tool name is the literal placeholder).
FORBIDDEN_BRANDS = ("EVsyst", "EVsystem")


@pytest.fixture()
def client():
    return TestClient(create_app())


def _get(client, path):
    resp = client.get(path)
    assert resp.status_code == 200, path
    return resp


def test_root_shell_has_tool_name_and_tagline(client):
    text = _get(client, "/").text
    assert "[TOOL NAME]" in text
    assert "Fleet electrification assistant" in text
    for brand in FORBIDDEN_BRANDS:
        assert brand not in text, brand


def test_root_shell_has_layout_landmarks(client):
    text = _get(client, "/").text
    # §5.2 shell landmarks that app.js and later steps hang off.
    assert "Assistant" in text
    assert "Drop files here \u2013 any format" in text or "Drop files here – any format" in text
    assert "Add sample files" in text
    assert "Drop your files" in text
    assert 'id="demo-pill"' in text
    # links to the self-hosted assets, not a CDN.
    assert "/css/app.css" in text
    assert "/js/app.js" in text


def test_css_served_and_fonts_are_local(client):
    css = _get(client, "/css/app.css").text
    assert "@font-face" in css
    # local font paths only.
    assert "/fonts/Barlow-Regular.ttf" in css
    assert "/fonts/BarlowCondensed-SemiBold.ttf" in css
    # NO external http(s) font / CDN URL anywhere in the CSS.
    assert "http://" not in css
    assert "https://" not in css
    assert "fonts.googleapis.com" not in css
    assert "fonts.gstatic.com" not in css


# §5.6 result-tab labels are fixed UI chrome from the spec (not registry-derived). a few of them
# coincide word-for-word with a registry section display_name (e.g. the "Charging" tab vs the
# "Charging" input section). the no-hardcoded-section-name guard below is scoped to EXCLUDE those
# §5.6 tab labels so a legitimate tab title does not trip it; the guard still proves the JS does not
# bake in the registry section list (it must come from /api/inputs - see the payload.sections check).
SECTION_NAME_GUARD_ALLOW = {
    # §5.6 result-tab labels:
    "Inputs",
    "Overview",
    "Energy",
    "Charging",
    "Grid & flexibility",
    "Costs (TCO)",
    "Scenarios",
    "Report",
    "Audit trail",
    # §5.5 scenario-bar control label that reuses a section word ("Weather"):
    "Weather",
}


def test_js_served_and_has_no_hardcoded_section_names(client):
    js = _get(client, "/js/app.js").text
    # §0: no registry section display_name may be baked into the JS as the source of the Inputs cards;
    # it must come from /api/inputs. §5.6 result-tab labels that happen to reuse a section word are
    # allow-listed above so a legitimate tab title is not mistaken for a hard-coded section name.
    for section in SECTIONS:
        if section.display_name in SECTION_NAME_GUARD_ALLOW:
            continue
        assert section.display_name not in js, section.display_name
    # the section cards are rendered from the server payload, not a hard-coded list.
    assert "payload.sections" in js
    # no hard-coded registry count / the old mock-up 112.
    assert "112" not in js
    assert not re.search(r"\btotal_inputs\s*=\s*\d", js)


def test_js_does_not_duplicate_the_opening_line(client):
    # §0 dumb client: the exact §4 opening string lives ONLY in hdev/intake_api.OPENING_LINE and is
    # rendered from the server payload. the served JS must NOT carry a duplicate literal (which could
    # drift from the server constant). check both the raw line and its \u-escaped form, plus the
    # distinctive tail, so a re-introduced OPENING_FALLBACK is caught.
    js = _get(client, "/js/app.js").text
    assert OPENING_LINE not in js
    escaped = OPENING_LINE.replace("\u2013", "\\u2013")
    assert escaped not in js
    # the distinctive closing sentence of the opening line must not be baked in as a JS literal.
    assert "No GPS needed." not in js


def test_js_does_no_arithmetic_on_server_numbers(client):
    # §0: the client must not derive displayed numbers. the removed helpers were a pct(part/whole*100)
    # ratio and a per-section (from_data + standard) running sum for the header tick; both are now
    # server numbers (from_data_pct / standard_pct / cumulative_found). guard against their return.
    js = _get(client, "/js/app.js").text
    assert "part / whole" not in js
    assert "* 100" not in js
    assert "/ total" not in js
    assert "from_data + section.standard" not in js
    assert "section.from_data + section.standard" not in js


def test_fonts_ofl_licence_served(client):
    text = _get(client, "/fonts/OFL.txt").text
    assert "SIL Open Font License" in text


def test_font_binaries_served(client):
    # the self-hosted .ttf files load over the static mount (works offline).
    for name in (
        "Barlow-Regular.ttf",
        "Barlow-Medium.ttf",
        "Barlow-SemiBold.ttf",
        "BarlowCondensed-SemiBold.ttf",
        "BarlowCondensed-Bold.ttf",
    ):
        resp = client.get("/fonts/" + name)
        assert resp.status_code == 200, name
        assert len(resp.content) > 1000, name


# ---- Step 5: run screen, tabs, charts, scenario bar guards --------------------------------------

# the ten §5.6 tab labels, in order. these are fixed UI chrome labels (not registry section names).
TAB_LABELS = (
    "Inputs",
    "Overview",
    "Energy",
    "Charging",
    "Grid &amp; flexibility",  # the ampersand is HTML-escaped when rendered; check both forms below
    "Costs (TCO)",
    "CO\u2082",
    "Scenarios",
    "Report",
    "Audit trail",
)

# the nine §5.3 run-screen checklist strings, verbatim.
CHECKLIST_STRINGS = (
    "Reading routes and stops",
    "Simulating 250 working days per truck",
    "Adding weather for every day of the year",
    "Sizing batteries to the hardest day",
    "Testing charging strategies",
    "Checking the depot grid connection",
    "Finding flexibility",
    "Calculating total cost of ownership",
    "Calculating CO\u2082",
)

# the four §5.5 recalculation overlay rotating lines.
RECALC_LINES = (
    "Re-running the year\u2026",
    "Re-sizing chargers\u2026",
    "Checking the grid\u2026",
    "Updating costs\u2026",
)

# chart libraries that must NEVER be referenced (charts are hand-drawn inline SVG, no canvas).
FORBIDDEN_CHART_LIBS = ("chart.js", "chartjs", "d3", "highcharts", "plotly", "echarts", "canvas")


def test_js_has_all_ten_tab_labels(client):
    js = _get(client, "/js/app.js").text
    # the tab labels live in the JS as plain UI copy (not registry section names). the ampersand tab
    # is stored unescaped in JS source, so check the raw "Grid & flexibility".
    for label in (
        "Inputs",
        "Overview",
        "Energy",
        "Charging",
        "Grid & flexibility",
        "Costs (TCO)",
        "CO\u2082",
        "Scenarios",
        "Report",
        "Audit trail",
    ):
        assert label in js, label


def test_js_has_tab_and_panel_roles(client):
    # §5.7 accessibility: tabs use role=tab + aria-selected; panels use role=tabpanel.
    js = _get(client, "/js/app.js").text
    assert 'role", "tab"' in js or '"tab"' in js
    assert "aria-selected" in js
    assert 'role", "tabpanel"' in js or '"tabpanel"' in js


def test_js_charts_are_accessible_images(client):
    # every chart <svg> carries role=img + a descriptive aria-label.
    js = _get(client, "/js/app.js").text
    assert 'role", "img"' in js or '"img"' in js
    assert "aria-label" in js


def test_js_uses_no_chart_library(client):
    # charts are hand-drawn inline stroke SVG. no chart library and no canvas may be referenced.
    js = _get(client, "/js/app.js").text.lower()
    for lib in FORBIDDEN_CHART_LIBS:
        assert lib not in js, lib


def test_js_has_run_screen_checklist_strings(client):
    js = _get(client, "/js/app.js").text
    for line in CHECKLIST_STRINGS:
        assert line in js, line
    # the run-screen title + subtitle + the done line template.
    assert "Running your fleet through a full year" in js
    assert "Every working day, every season, every truck." in js
    assert "truck-days simulated" in js


def test_js_has_recalculation_overlay_strings(client):
    js = _get(client, "/js/app.js").text
    assert "Recalculating" in js
    for line in RECALC_LINES:
        assert line in js, line


def test_js_shows_human_priority_labels_not_internal_keys(client):
    # §8: internal priority keys cost/grid/early must never be the representation; the human labels
    # Lowest cost / Grid-friendly / Ready earliest are shown instead. the client-facing enum names
    # (lowest_cost etc.) are allowed because they are posted back as raw lever values, but each must
    # map to a human label.
    js = _get(client, "/js/app.js").text
    assert "Lowest cost" in js
    assert "Grid-friendly" in js
    assert "Ready earliest" in js
    # the internal mock-up keys never appear as standalone priority tokens in the client JS.
    assert '"cost"' not in js
    assert '"grid"' not in js
    assert '"early"' not in js


def test_js_overview_working_days_comes_from_server(client):
    # §0: the Overview "based on" chip must read the server's working_days field, not a baked-in
    # literal. the plain substring "250 working days" cannot simply be banned because the §5.3
    # run-screen checklist legitimately contains the copy string "Simulating 250 working days per
    # truck" (fixed narrative, not a rendered datum). So assert two precise things instead:
    #   1. the JS reads payload.working_days (the chip is server-sourced), and
    #   2. the old chip literal that combined 250 with the "weather included" copy is gone.
    # The checklist copy does not contain "working days \u00b7 weather included", so this ban is
    # precise and does not collide with it.
    js = _get(client, "/js/app.js").text
    assert "working_days" in js
    # the chip wording lives in source as a \u00b7 escape (literal backslash-u), so match that form.
    assert "250 working days \\u00b7 weather included" not in js
    # the "weather included" wording stays as copy (only the number is server-sourced).
    assert "working days \\u00b7 weather included" in js


def test_js_scaling_arithmetic_is_only_in_svg_helpers(client):
    # §0 no-business-maths guard, scoped. the earlier guard (test_js_does_no_arithmetic_on_server_numbers)
    # bans the specific data-handling arithmetic markers. Step 5 adds SVG coordinate scaling, which is
    # drawing layout, not business maths - the earlier guard patterns ('part / whole', '* 100',
    # '/ total', the from_data+standard sums) must still be absent even with the chart helpers present.
    js = _get(client, "/js/app.js").text
    assert "part / whole" not in js
    assert "/ total" not in js
    assert "section.from_data + section.standard" not in js


def test_no_method_hiding_leaks_in_static_assets(client):
    # §8: no maps_to and no collapsed-field id/label may appear in any served static asset.
    html = _get(client, "/").text
    css = _get(client, "/css/app.css").text
    js = _get(client, "/js/app.js").text
    blob = html + css + js
    assert "maps_to" not in blob
    for f in FIELDS:
        assert f.maps_to not in blob, f.id
    for f in counted_only_fields():
        assert f.id not in blob, f.id
        assert f.label not in blob, f.label
