# STATUS: NEW (Step 9, items 1-3). Tests for the resolver front-end:
#   - waypoint_parser: parse_vdri_text / parse_vacc_text (M0.0)
#   - defaults:        per-value {value, source, label}; CdxA default None + flagged (M1.1)
#   - resolve_typed:   typed summary -> even-spaced waypoints with the HDEV assumption flagged (M4.3)
# conftest.py puts repo root on sys.path so imports resolve as src.resolver.*

import pytest

from src.resolver.waypoint_parser import (
    Waypoint, VaccPoint, parse_vdri_text, parse_vacc_text,
)
from src.resolver import defaults as D
from src.resolver.resolve_typed import resolve_typed


# ---------------------------------------------------------------------------
# ITEM 1 - waypoint + .vacc parser
# ---------------------------------------------------------------------------

# a small pasted VDRI with a header, a comment and a blank line to be skipped.
VDRI_SAMPLE = """<s>,<v>,<grad>,<stop>
0,0,0.6,45.4
# a comment row
1,34.4,0.6,0

101,29.9,0.8,0
"""

VACC_SAMPLE = """v [km/h],acc [m/s2],dec [m/s2]
60,0.5,-0.5
0,1,-1
25,1,-1
"""


def test_parse_vdri_text_expected_waypoints():
    wps = parse_vdri_text(VDRI_SAMPLE)
    # header, comment and blank rows dropped -> 3 waypoints
    assert len(wps) == 3
    assert all(isinstance(w, Waypoint) for w in wps)
    # row 0: distance 0, speed 0, grade 0.6, stop 45.4
    assert wps[0].distance == 0.0
    assert wps[0].speed == 0.0
    assert wps[0].grade_pct == 0.6
    assert wps[0].stop == 45.4
    # row 1
    assert wps[1].distance == 1.0
    assert wps[1].speed == 34.4
    assert wps[1].stop == 0.0
    # row 2
    assert wps[2].distance == 101.0
    assert wps[2].speed == 29.9
    assert wps[2].grade_pct == 0.8


def test_parse_vdri_attributes_match_driver_model():
    # the driver model reads .distance, .speed, .stop, .grade_pct - confirm they exist
    w = parse_vdri_text(VDRI_SAMPLE)[0]
    for attr in ("distance", "speed", "stop", "grade_pct"):
        assert hasattr(w, attr)


def test_parse_vacc_text_sorts_and_parses():
    pts = parse_vacc_text(VACC_SAMPLE)
    assert len(pts) == 3
    assert all(isinstance(p, VaccPoint) for p in pts)
    # sorted ascending by speed: 0, 25, 60
    assert [p.speed for p in pts] == [0.0, 25.0, 60.0]
    assert pts[0].acc == 1.0 and pts[0].dec == -1.0
    assert pts[2].acc == 0.5 and pts[2].dec == -0.5
    # the driver model reads .speed, .acc, .dec
    for attr in ("speed", "acc", "dec"):
        assert hasattr(pts[0], attr)


def test_parsers_raise_on_empty_input():
    with pytest.raises(ValueError):
        parse_vdri_text("")
    with pytest.raises(ValueError):
        parse_vdri_text("<s>,<v>,<grad>,<stop>\n# only header and comment\n")
    with pytest.raises(ValueError):
        parse_vacc_text("")
    with pytest.raises(ValueError):
        parse_vacc_text("   \n\n")


# ---------------------------------------------------------------------------
# ITEM 2 - defaults.py
# ---------------------------------------------------------------------------

def _all_entries():
    # collect every {value, source, label} entry across the module's default tables
    entries = []
    for name in dir(D):
        obj = getattr(D, name)
        if isinstance(obj, dict) and obj.get("source") is not None and "label" in obj:
            entries.append((name, obj))
        elif isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, dict) and "value" in v and "source" in v and "label" in v:
                    entries.append(("%s[%r]" % (name, k), v))
    return entries


def test_every_default_entry_has_value_source_label():
    entries = _all_entries()
    assert entries, "expected default entries to be found"
    for name, e in entries:
        assert set(("value", "source", "label")).issubset(e.keys()), name
        assert e["label"] in D.LABELS, "%s has bad label %r" % (name, e["label"])
        assert isinstance(e["source"], str) and e["source"], name


def test_cdxa_default_is_none_and_flagged():
    # 🔒 M1.1: every CdxA default must be None and explicitly flagged as having no source
    for group, entry in D.CDXA_DEFAULT_M2.items():
        assert entry["value"] is None, "CdxA group %s must be None (locked)" % group
        assert "missing" in entry["source"].lower() or "no source" in entry["source"].lower()
    # construction column too
    assert D.CDXA_DEFAULT_CONSTRUCTION_M2["5"]["value"] is None
    # the SegmentTable numbers must NOT have been copied in as usable values
    assert not D.is_sourced(D.CDXA_DEFAULT_M2["5"])


def test_vecto_neutral_params_and_known_values():
    assert D.NEUTRAL_PARAMS["beta"]["value"] == 1.0
    assert D.NEUTRAL_PARAMS["theta_red"]["value"] == 0.0
    # VECTO beta 0.9 cited separately
    assert D.NEUTRAL_PARAMS["beta_vecto"]["value"] == 0.9
    assert D.NEUTRAL_PARAMS["beta_vecto"]["label"] == D.VECTO
    # a couple of transcribed p_aux electric values
    assert D.PAUX_ES_HEAVY_STANDARD_W["LH"]["value"] == 1200.0
    assert D.PAUX_ES_HEAVY_STANDARD_W["RD"]["value"] == 1000.0
    assert D.PAUX_COND_W["LH"]["value"] == 600.0
    assert D.DESIGN_SPEED_KMH["value"] == 85.0


def test_typed_resolver_defaults_are_flagged_assumptions():
    for key in ("cruise_speed_deep_urban_kmh", "dwell_s", "grade_pct", "even_stop_spacing"):
        assert D.TYPED_RESOLVER[key]["label"] == D.HDEV_ASSUMPTION


def test_get_accessor_raises_on_missing_key():
    with pytest.raises(KeyError):
        D.get(D.PAUX_COND_W, "NOPE")


# ---------------------------------------------------------------------------
# ITEM 3 - resolve_typed
# ---------------------------------------------------------------------------

def test_resolve_typed_even_spacing():
    out = resolve_typed(
        total_distance_m=30000.0,
        n_stops=3,
        avg_stop_duration_s=60.0,
        cruise_speed_kmh=50.0,
        grade_pct=0.0,
    )
    wps = out["waypoints"]
    # 3 stops -> 4 waypoints (depot + 3 stops), evenly spaced at 0 / 10000 / 20000 / 30000
    assert [w.distance for w in wps] == [0.0, 10000.0, 20000.0, 30000.0]
    # depot carries no stop; the 3 stops carry the dwell
    assert wps[0].stop == 0.0
    assert [w.stop for w in wps[1:]] == [60.0, 60.0, 60.0]
    # all waypoints have the cruise speed and flat grade
    assert all(w.speed == 50.0 for w in wps)
    assert all(w.grade_pct == 0.0 for w in wps)
    # output shape matches the parser waypoints (same attributes)
    assert isinstance(wps[0], Waypoint)


def test_resolve_typed_flags_even_spacing_assumption():
    out = resolve_typed(30000.0, 3, 60.0, 50.0)
    joined = " ".join(out["assumptions"]).lower()
    assert "even stop spacing" in joined
    # speed-wins-over-end-time is also recorded
    assert "speed wins over end time" in joined
    # the defaults used are reported back
    assert out["defaults_used"]["cruise_speed_kmh"] == 50.0


def test_resolve_typed_no_stops():
    out = resolve_typed(12000.0, 0, 0.0, 80.0)
    wps = out["waypoints"]
    assert [w.distance for w in wps] == [0.0, 12000.0]
    assert all(w.stop == 0.0 for w in wps)


def test_resolve_typed_raises_on_invalid_input():
    with pytest.raises(ValueError):
        resolve_typed(-1.0, 3, 60.0, 50.0)          # negative distance
    with pytest.raises(ValueError):
        resolve_typed(30000.0, -1, 60.0, 50.0)      # negative stops
    with pytest.raises(ValueError):
        resolve_typed(30000.0, 3, 60.0, 0.0)        # non-positive speed
    with pytest.raises(ValueError):
        resolve_typed(30000.0, 3, -5.0, 50.0)       # negative dwell
