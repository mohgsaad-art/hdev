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


def test_js_served_and_has_no_hardcoded_section_names(client):
    js = _get(client, "/js/app.js").text
    # §0: no section display_name may be baked into the JS; it must come from /api/inputs.
    for section in SECTIONS:
        assert section.display_name not in js, section.display_name
    # no hard-coded registry count / the old mock-up 112.
    assert "112" not in js
    assert not re.search(r"\btotal_inputs\s*=\s*\d", js)


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
