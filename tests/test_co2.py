# STATUS: NEW (Step 9, item 18 / 🔒 M6.25, Bob to review). CO2 interface + stub tests.
#
# The sources (LCA factors + grid emission-factor series) are locked by M6.25, so co2_result returns a
# null-filled structure with the demo-matching client-facing keys, and the strict variant raises.
import json

import pytest

from src.server import co2


def test_co2_result_returns_null_filled_structure():
    r = co2.co2_result(annual_energy_kwh=100000.0, annual_diesel_litres=50000.0,
                       battery_kwh=300.0, ownership_years=10)
    # demo-matching client-facing keys, all null.
    assert r["diesel_t_per_year"] is None
    assert r["electric_t_per_year"] is None
    assert r["available"] is False
    # the cumulative series is shaped for the chart (years+1 points) but every point is null.
    assert r["cumulative_saved_t"] == [None] * 11


def test_co2_result_no_years_gives_null_series():
    r = co2.co2_result()
    assert r["cumulative_saved_t"] is None
    assert r["available"] is False


def test_co2_result_strict_raises_blocked_by_m625():
    with pytest.raises(NotImplementedError) as ei:
        co2.co2_result_strict()
    assert "M6.25" in str(ei.value)


def test_co2_output_is_plain_worded():
    # §8: no LCA source name / emission-factor coefficient on the client-facing surface. The `flag`
    # string names the lock (M6.25) in plain words, which is allowed as a provenance note.
    r = co2.co2_result(ownership_years=5)
    surface = json.dumps({k: r[k] for k in ("diesel_t_per_year", "electric_t_per_year", "cumulative_saved_t")})
    for banned in ("ICCT", "IVL", "Energinet", "emission-factor", "well-to-wheel"):
        assert banned not in surface
